from sqlmodel import create_engine, SQLModel
from backend.config import settings

engine = create_engine(settings.SQLMODEL_DATABASE_URL)
SQLModel.metadata.create_all(engine)