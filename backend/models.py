from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.sql import func

from db import Base


class User(Base):
    """BRD roles: platform_admin | agency_client | end_customer."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="agency_client", index=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Campaign(Base):
    """Lifecycle: draft → pending_approval → pending_payment → paid → active → completed | failed."""

    __tablename__ = "campaigns"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft", index=True)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    celery_task_id = Column(String, nullable=True, index=True)
    stripe_checkout_session_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class JobAudit(Base):
    """Audit trail for async media jobs (Celery task id ↔ provider ↔ request id)."""

    __tablename__ = "job_audits"

    id = Column(String, primary_key=True)
    celery_task_id = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)
    request_id = Column(String, nullable=False, index=True)
    input_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
