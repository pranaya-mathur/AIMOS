from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, Numeric, String
from sqlalchemy.sql import func

from db import Base


class Organization(Base):
    """Multi-office / multi-tenant boundary."""

    __tablename__ = "organizations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    
    # Milestone 5: Whitelabeling (AIM-170)
    whitelabel_config = Column(JSON, nullable=True) # { "logo_url": "...", "primary_color": "...", "site_name": "..." }
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AuditLog(Base):
    """Enterprise Audit Trail (AIM-165)."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True) # e.g. "CAMPAIGN_LAUNCH", "BRAND_KIT_GEN"
    resource_id = Column(String, nullable=True, index=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    """BRD roles: platform_admin | agency_client | end_customer."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="agency_client", index=True)
    full_name = Column(String, nullable=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    is_onboarded = Column(String, nullable=False, default="false", server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # Subscription billing
    subscription_tier = Column(String, nullable=False, default="free", server_default="free", index=True)
    subscription_status = Column(String, nullable=False, default="none", server_default="none", index=True)
    stripe_customer_id = Column(String, nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String, nullable=True, unique=True, index=True)
    # Per-user overrides: NULL → server default from env; -1 → unlimited for that dimension.
    monthly_campaign_quota = Column(Integer, nullable=True)
    monthly_token_quota = Column(Integer, nullable=True)


class Brand(Base):
    """Seller brand profile and onboarding data."""

    __tablename__ = "brands"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Brand Identity (AIM-006)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # Assets & Links (AIM-007, AIM-008, AIM-009)
    logo_url = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    social_links = Column(JSON, nullable=True)  # { "instagram": "...", "facebook": "...", ... }
    
    # Strategy & Targeting (AIM-010, AIM-011, AIM-012)
    target_audience = Column(JSON, nullable=True)  # { "age": "...", "gender": "...", "location": "...", "interests": "..." }
    product_details = Column(JSON, nullable=True)  # List of products/services
    pricing_range = Column(String, nullable=True)  # budget | mid | premium
    
    # Onboarding Selections (AIM-001 to AIM-005)
    business_type = Column(String, nullable=True)  # D2C | Service | Creator | Local Business
    industry = Column(String, nullable=True)
    marketing_goal = Column(String, nullable=True) # Sales | Leads | Awareness
    monthly_budget = Column(Numeric(12, 2), nullable=True)
    platform_preference = Column(JSON, nullable=True) # ["meta", "google"]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Campaign(Base):
    """Lifecycle: draft → pending_approval → pending_payment → paid → active → completed | failed | rejected."""

    __tablename__ = "campaigns"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft", index=True)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    celery_task_id = Column(String, nullable=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    stripe_checkout_session_id = Column(String, nullable=True)

    # Added for Milestone 3 (AIM-060+)
    platform = Column(String, default="both")
    objective = Column(String, default="leads")
    total_budget = Column(Float, default=0.0)
    schedule_start = Column(DateTime, nullable=True)
    schedule_end = Column(DateTime, nullable=True)

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


class UsageEvent(Base):
    """Append-only AI usage for quota + cost reporting (OpenAI token counts)."""

    __tablename__ = "usage_events"
    __table_args__ = (Index("ix_usage_events_user_created", "user_id", "created_at"),)

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String, nullable=False, index=True)
    model = Column(String, nullable=True)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Numeric(12, 6), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class MediaAsset(Base):
    """Storage for AI generated media (AIM-081)."""

    __tablename__ = "media_assets"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String, nullable=False, index=True) # adcreative | pictory | elevenlabs
    asset_type = Column(String, nullable=False, index=True) # card | video | audio
    url = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Milestone 4: Lead Intelligence
    status = Column(String, default="new")  # new, contacted, qualified, lost, closed
    score = Column(Integer, default=0)
    intent = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    
    lead_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True)
    lead_id = Column(String, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    direction = Column(String, nullable=False)  # inbound | outbound
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CampaignMetric(Base):
    """Daily performance snapshots for optimization."""

    __tablename__ = "campaign_metrics"

    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    day = Column(Date, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # meta | google | x

    spend = Column(Numeric(12, 4), default=0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_metrics_campaign_day", "campaign_id", "day"),)
