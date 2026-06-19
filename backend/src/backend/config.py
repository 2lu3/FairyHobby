from uuid import UUID

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

    # dev 環境の /docs から API を試すときに使う既定ユーザー（任意）
    DOCS_BYPASS_USER_ID: UUID | None = None
    DOCS_BYPASS_FIREBASE_UID: str | None = None


settings = Settings()
