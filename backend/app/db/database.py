from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


try:
    from app.db.models import Base as ModelsBase

    ModelsBase.metadata.create_all(bind=engine)
except Exception:
    pass


def create_db_and_tables() -> None:
    from app.db.models import Base as ModelsBase

    ModelsBase.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
