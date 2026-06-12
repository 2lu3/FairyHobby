from time import struct_time
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    GOOGLE_APPLICATION_CREDENTIALS: str

    @computed_field
    @property
    def SQLMODEL_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
