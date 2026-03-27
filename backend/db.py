from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def apply_schema_patches() -> None:
    """Idempotent ALTERs for existing DBs (create_all does not add new columns)."""
    if engine.dialect.name != "postgresql":
        return
    stmts = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_campaign_quota INTEGER",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_token_quota INTEGER",
    ]
    with engine.begin() as conn:
        for sql in stmts:
            conn.execute(text(sql))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
