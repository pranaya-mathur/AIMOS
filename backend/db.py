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
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id VARCHAR REFERENCES organizations(id) ON DELETE SET NULL",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS organization_id VARCHAR REFERENCES organizations(id) ON DELETE SET NULL",
        # Subscription billing columns
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR NOT NULL DEFAULT 'free'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR NOT NULL DEFAULT 'none'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR UNIQUE",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR UNIQUE",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_onboarded VARCHAR NOT NULL DEFAULT 'false'",
        # Milestone 2: Media Assets
        "CREATE TABLE IF NOT EXISTS media_assets (id TEXT PRIMARY KEY, user_id TEXT, campaign_id TEXT, provider TEXT, asset_type TEXT, url TEXT, metadata_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        # Milestone 3: Campaign Enhancements
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS platform VARCHAR DEFAULT 'both'",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS objective VARCHAR DEFAULT 'leads'",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS total_budget FLOAT DEFAULT 0.0",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS schedule_start TIMESTAMP",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS schedule_end TIMESTAMP",
        # Milestone 4: Lead Intelligence
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS user_id VARCHAR REFERENCES users(id) ON DELETE SET NULL",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'new'",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS intent VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS sentiment VARCHAR",
        # Milestone 5: Enterprise Governance & Whitelabeling
        "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS whitelabel_config TEXT",
        "CREATE TABLE IF NOT EXISTS audit_logs (id TEXT PRIMARY KEY, user_id TEXT, organization_id TEXT, action TEXT, resource_id TEXT, metadata_json TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
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
