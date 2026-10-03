from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

_settings = get_settings()
_kwargs = {"pool_pre_ping": True, "pool_recycle": 1800}
if _settings.sqlalchemy_url.startswith("sqlite"):
    _kwargs = {}
engine = create_engine(_settings.sqlalchemy_url, connect_args=_settings.connect_args, **_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
