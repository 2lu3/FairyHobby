from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_ENV: str  # dev / prod

    # 明示指定が無い場合は APP_ENV から決定する (dev=DEBUG / prod=INFO)
    LOG_LEVEL: str | None = "DEBUG"

    API_V1_STR: str = "/api/v1"

    SESSION_SECRET_KEY: str

    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    GOOGLE_CLOUD_PROJECT_ID: str
    GOOGLE_CLOUD_SQL_REGION: str
    GOOGLE_CLOUD_SQL_INSTANCE_NAME: str

    GOOGLE_CLOUD_STORAGE_BUCKET_NAME: str = "fairyhobby"

    # ローカル開発用エミュレータ設定 (本番では未設定)
    # 設定されている場合、Cloud Storage の代わりに fake-gcs-server を利用する。
    # google-cloud-storage クライアントは環境変数 STORAGE_EMULATOR_HOST を自動参照する。
    STORAGE_EMULATOR_HOST: str | None = None
    # ブラウザから到達可能な fake-gcs-server のエンドポイント (画像URLの生成に利用)
    GCS_PUBLIC_ENDPOINT: str | None = None
    # 設定されている場合、Firebase Auth Emulator を利用する。
    # firebase-admin は環境変数 FIREBASE_AUTH_EMULATOR_HOST を自動参照する。
    FIREBASE_AUTH_EMULATOR_HOST: str | None = None

    @computed_field
    @property
    def SQLMODEL_DATABASE_URL(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        if self.APP_ENV == "prod":
            return f"postgresql://{self.POSTGRES_USER}:{password}@/{self.POSTGRES_DB}?host=/cloudsql/{self.GOOGLE_CLOUD_PROJECT_ID}:{self.GOOGLE_CLOUD_SQL_REGION}:{self.GOOGLE_CLOUD_SQL_INSTANCE_NAME}"
        else:
            return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    GOOGLE_APPLICATION_CREDENTIALS: str | None = None

    FRONTEND_URL: str

    OPENAI_API_KEY: str

    # プラン名・説明の生成や嗜好プロファイル生成に利用するチャットモデル
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    # devの場合のみ設定する
    ADMIN_USER_ID: str | None = None
    ADMIN_STORE_ID: str | None = None


settings = Settings()
