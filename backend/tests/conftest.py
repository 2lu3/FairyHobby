import os
from pathlib import Path
from collections.abc import AsyncGenerator, Generator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session
from testcontainers.postgres import PostgresContainer
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine


# backend.config.Settings は必須環境変数を要求するため、
# backend.* を import する前にテスト用のダミー値を入れておく。
# （実際の DB は testcontainer、認証はオーバーライドで差し替えるので、
#   ここでの値はアプリ起動時に Settings を構築できれば十分。）
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/dev/null")

# tests/ の親 = backend/ プロジェクトルート
BACKEND_DIR = Path(__file__).resolve().parent.parent


# テストで「ログイン済み」として扱う firebase uid。
# get_firebase_uid をこの値を返すよう差し替える。
TEST_FIREBASE_UID = "test-firebase-uid"


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    """テスト用の使い捨て Postgres を立て、alembic でスキーマを構築した engine を返す。

    コンテナの起動とマイグレーションはテストセッション全体で 1 回だけ行う。
    """
    with PostgresContainer("postgres:16") as postgres:
        url = postgres.get_connection_url()  # postgresql+psycopg2://...

        # alembic env.py が DATABASE_URL を優先して読む実装になっているため、
        # ここで testcontainer の URL を注入してから upgrade head を流す。
        os.environ["DATABASE_URL"] = url
        alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(url)
        try:
            yield engine
        finally:
            engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    """各テストを外側トランザクションで包み、終了時に rollback して分離する。"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def firebase_uid() -> str:
    """テストで「ログイン中ユーザー」として扱う firebase uid。"""
    return TEST_FIREBASE_UID


@pytest.fixture(autouse=True)
def mock_openai_background_tasks(monkeypatch):
    """OpenAI 呼び出しを伴う background task をテスト中は無効化する。"""

    def _noop(*args, **kwargs):
        if args:
            return args[0]
        return None

    monkeypatch.setattr(
        "backend.activities.router.generate_preference_and_embeddings", _noop
    )
    monkeypatch.setattr(
        "backend.activity_reviews.router.generate_preference_and_embeddings", _noop
    )
    monkeypatch.setattr("backend.fairies.router.generate_embeddings", _noop)


@pytest.fixture
def logged_in_user(db_session: Session, firebase_uid: str):
    """認証が必要なエンドポイント向けに、ログイン済みユーザーを DB に投入する。"""
    from backend.users.models import User

    user = User(
        firebase_uid=firebase_uid,
        email="test@example.com",
        display_name="Test User",
        icon="🙂",
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
async def client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    """依存を差し替えた状態の ASGI クライアント。

    - get_db_session    -> テスト用 db_session (rollback される)
    - get_firebase_uid  -> TEST_FIREBASE_UID を返す (Firebase 検証を回避)
    - get_current_user  -> TEST_FIREBASE_UID のユーザーを返す (未登録なら 404)
    """
    from sqlmodel import select

    from backend.auth.dependencies import get_firebase_uid
    from backend.database import get_db_session
    from backend.exceptions import NotFoundError
    from backend.main import app
    from backend.users.dependencies import get_current_user
    from backend.users.models import User

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    def override_get_firebase_uid() -> str:
        return TEST_FIREBASE_UID

    def override_get_current_user() -> User:
        user = db_session.exec(
            select(User).where(User.firebase_uid == TEST_FIREBASE_UID)
        ).first()
        if not user:
            raise NotFoundError()
        return user

    app.dependency_overrides[get_db_session] = override_get_session
    app.dependency_overrides[get_firebase_uid] = override_get_firebase_uid
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()
