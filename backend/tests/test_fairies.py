"""fairies エンドポイントのテスト。"""

from dataclasses import dataclass, field

import pytest
from sqlmodel import Session

from backend.fairies.models import Fairy
from backend.fairies.service import create as create_fairy_service


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


@dataclass
class FakeBlob:
    path: str
    uploaded_bytes: bytes | None = None
    content_type: str | None = None

    def upload_from_string(self, data: bytes, content_type: str | None = None) -> None:
        self.uploaded_bytes = data
        self.content_type = content_type

    @property
    def public_url(self) -> str:
        return f"https://storage.example.com/{self.path}"


@dataclass
class FakeBucket:
    blobs: dict[str, FakeBlob] = field(default_factory=dict)

    def blob(self, path: str) -> FakeBlob:
        if path not in self.blobs:
            self.blobs[path] = FakeBlob(path=path)
        return self.blobs[path]


@pytest.fixture
def mock_storage(monkeypatch):
    """GCS へのアップロードをメモリ上の FakeBucket に差し替える。"""
    bucket = FakeBucket()

    monkeypatch.setattr("backend.fairies.service.get_bucket", lambda: bucket)
    monkeypatch.setattr(
        "backend.fairies.schemas.get_presigned_url",
        lambda path: f"https://storage.example.com/{path}",
    )
    return bucket


def test_create_fairy_service(db_session: Session, mock_storage: FakeBucket):
    """create サービスが DB 保存とストレージアップロードを行う。"""
    fairy = create_fairy_service(
        "Luna",
        "A moon fairy",
        PNG_BYTES,
        "image/png",
        db_session,
    )

    assert fairy.name == "Luna"
    assert fairy.prompt == "A moon fairy"
    assert fairy.image_content_type == "image/png"
    assert fairy.image_path == f"fairies/{fairy.id}.png"

    stored = db_session.get(Fairy, fairy.id)
    assert stored is not None
    assert stored.name == "Luna"

    blob = mock_storage.blobs[fairy.image_path]
    assert blob.uploaded_bytes == PNG_BYTES
    assert blob.content_type == "image/png"


async def test_create_fairy(client, db_session, logged_in_user, mock_storage):
    """POST /fairies でフェアリーを作成する。"""
    res = await client.post(
        "/fairies",
        data={"name": "Luna", "prompt": "A moon fairy"},
        files={"image": ("luna.png", PNG_BYTES, "image/png")},
    )

    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "Luna"
    assert body["prompt"] == "A moon fairy"
    assert body["image_url"] == f"https://storage.example.com/fairies/{body['id']}.png"

    created = db_session.get(Fairy, body["id"])
    assert created is not None
    assert created.image_path == f"fairies/{body['id']}.png"

    blob = mock_storage.blobs[created.image_path]
    assert blob.uploaded_bytes == PNG_BYTES
    assert blob.content_type == "image/png"


async def test_create_fairy_not_found_when_user_absent(client, mock_storage):
    """DB にユーザーがいなければ 404。"""
    res = await client.post(
        "/fairies",
        data={"name": "Luna", "prompt": "A moon fairy"},
        files={"image": ("luna.png", PNG_BYTES, "image/png")},
    )
    assert res.status_code == 404


async def test_update_fairy(client, db_session, logged_in_user, mock_storage):
    """PATCH /fairies/{id} がフェアリーを更新する。"""
    created = await client.post(
        "/fairies",
        data={"name": "Luna", "prompt": "A moon fairy"},
        files={"image": ("luna.png", PNG_BYTES, "image/png")},
    )
    assert created.status_code == 201
    fairy_id = created.json()["id"]

    res = await client.patch(
        f"/fairies/{fairy_id}",
        json={"name": "Sol", "prompt": "A sun fairy"},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Sol"
    assert body["prompt"] == "A sun fairy"
    assert body["image_url"] == f"https://storage.example.com/fairies/{fairy_id}.png"

    updated = db_session.get(Fairy, fairy_id)
    assert updated is not None
    assert updated.name == "Sol"
    assert updated.prompt == "A sun fairy"
