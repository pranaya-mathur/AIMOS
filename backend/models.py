from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, Numeric, String, Boolean, Text
from sqlalchemy.sql import func

from db import Base


class Organization(Base):
    """Multi-office / multi-tenant boundary."""

    __tablename__ = "organizations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    
    # Milestone 5: Whitelabeling (AIM-170)
    whitelabel_config = Column(JSON, nullable=True) # { "logo_url": "...", "primary_color": "...", "site_name": "..." }
    
    # Enterprise Seats (AIM-160)
    monthly_seat_quota = Column(Integer, default=1, server_default="1")
    
    # Hardened 2.0 Orchestration Controls (AIM-200)
    max_orchestration_iterations = Column(Integer, default=3, server_default="3")
    manual_intervention_enabled = Column(Boolean, default=True, server_default="true")
    
    # Hardened 2.0 Option B: Autonomous Autopilot (AIM-220)
    autopilot_enabled = Column(Boolean, default=False, server_default="false")
    autopilot_max_shift_percent = Column(Float, default=5.0, server_default="5.0")
    autopilot_max_shift_amount = Column(Float, default=100.0, server_default="100.0")
    
    # Hardened 2.0 Phase 7: Team Governance (AIM-165)
    # { "senior_approval_threshold_amount": 500, "senior_approval_threshold_percent": 20 }
    governance_settings = Column(JSON, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TeamInvite(Base):
    """Track pending team invitations (AIM-160)."""

    __tablename__ = "team_invites"

    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(String, default="agency_client") # agency_client | end_customer
    
    status = Column(String, default="pending") # pending | accepted | expired
    token = Column(String, unique=True, index=True)
    
class ProcessedStripeEvent(Base):
    """Idempotency log for Stripe webhooks (AIM-155)."""
    __tablename__ = "processed_stripe_events"
    id = Column(String, primary_key=True) # Stripe Event ID (evt_xxx)
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
    
    # Hardened 2.0 Phase 2: Unified Seller Profile (AIM-001-005)
    business_type = Column(String, nullable=True) # D2C | SaaS | Creator | Local
    industry = Column(String, nullable=True) # Fashion | Dental | Real Estate etc.
    primary_goal = Column(String, nullable=True) # Leads | Sales | Awareness
    monthly_budget = Column(Float, nullable=True)
    platform_preference = Column(String, nullable=True) # Meta | Google | Both
    
    # Context
    description = Column(Text, nullable=True)
    website_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BrandWisdom(Base):
    """Hardened 2.0 Phase 5: Long-term cross-campaign learning logs."""

    __tablename__ = "brand_wisdom"

    id = Column(String, primary_key=True)
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # "creative_performance" | "budget_efficiency" | "audience_behavior" | "manual_constraint"
    insight_type = Column(String, nullable=False, index=True)
    
    content = Column(Text, nullable=False) # e.g. "Emoji-heavy hooks in Real Estate industry have 20% higher CTR"
    
    impact_score = Column(Integer, default=50) # 0-100 magnitude
    
    # { "industry": "Fashion", "goal": "Sales", "platform": "Meta" }
    context_tags = Column(JSON, nullable=True)
    
    is_global = Column(Boolean, default=False) # Potential for cross-brand learning
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CompetitorIntel(Base):
    """Hardened 2.0 Phase 2: Real-world competitor research snapshots."""

    __tablename__ = "competitor_intel"

    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=True, index=True)
    
    competitor_name = Column(String, nullable=False)
    competitor_url = Column(String, nullable=True)
    
    # The Intelligence Payload
    positioning = Column(Text, nullable=True)
    ad_hooks = Column(JSON, nullable=True) # List of hooks/copy identified
    pricing_notes = Column(Text, nullable=True)
    
    risk_to_client = Column(Integer, default=50) # 0-100 score
    last_researched_at = Column(DateTime(timezone=True), server_default=func.now())
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

    # AI Persisted Strategy (Milestone 1/2 Integration)
    ai_generated_kit = Column(JSON, nullable=True) # { "brand_narrative": "...", "brand_voice": "...", "color_palette": [...] }
    analysis_report = Column(JSON, nullable=True)  # Detailed competitor / audience analysis

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class EcomIntegration(Base):
    """Hardened 2.0 Phase 6: E-commerce store connections (Shopify/Woo)."""

    __tablename__ = "ecom_integrations"

    id = Column(String, primary_key=True)
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    
    provider = Column(String, nullable=False) # shopify | woocommerce
    store_url = Column(String, nullable=False)
    
    # Encrypted in production (simulated here)
    access_token = Column(String, nullable=True) 
    
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    """Hardened 2.0 Phase 6: Synchronized products from external stores."""

    __tablename__ = "products"

    id = Column(String, primary_key=True)
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    integration_id = Column(String, ForeignKey("ecom_integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    external_id = Column(String, nullable=False, index=True) # Shopify/WC ID
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=True)
    currency = Column(String, default="USD")
    
    image_url = Column(String, nullable=True)
    inventory_quantity = Column(Integer, default=0)
    
    # AI Control
    is_sync_enabled = Column(Boolean, default=True)
    last_processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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
    
    # Hardened 2.0 Orchestration (AIM-200)
    # { "iterations": 2, "history": ["content_studio", "optimization_engine", ...], "reasoning_log": ["..." ] }
    orchestration_metadata = Column(JSON, nullable=True)

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


class AdCreative(Base):
    """Structured ad copy variations (AIM-040)."""

    __tablename__ = "ad_creatives"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    
    headline = Column(String, nullable=True)
    body_copy = Column(String, nullable=True)
    cta_text = Column(String, nullable=True)
    
    # Optional link to a specific generated image/video
    media_asset_id = Column(String, ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True)
    
    status = Column(String, default="draft")  # draft | approved
    is_favorite = Column(String, default="false", server_default="false")
    
    # Hardened 2.0 Predictive Forecasting (AIM-210)
    # { "predicted_ctr": "...", "predicted_cpl": "...", "confidence_score": 85, "outlook": "high" }
    predicted_metrics = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


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
    
    # Conversion Attribution (AIM-118, AIM-119)
    landing_page_id = Column(String, ForeignKey("landing_pages.id", ondelete="SET NULL"), nullable=True, index=True)
    source = Column(String, nullable=True) # e.g. "facebook_ad", "organic", "google"
    
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

    # Optional creative attribution
    creative_id = Column(String, ForeignKey("ad_creatives.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_metrics_campaign_day", "campaign_id", "day"),)


class OptimizationDirective(Base):
    """Actionable AI suggestions for growth (AIM-060)."""

    __tablename__ = "optimization_directives"

    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    directive_type = Column(String, nullable=False) # pause | scale | shift | refresh
    description = Column(String, nullable=False)
    
    # { "budget_change": 0.2, "target_status": "PAUSED", "reason": "..." }
    suggested_payload = Column(JSON, nullable=True)
    
    status = Column(String, default="pending") # pending | scheduled | applied | dismissed
    applied_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Hardened 2.0 Autopilot Context (AIM-220)
    execution_mode = Column(String, default="manual") # manual | autopilot
    risk_score = Column(Integer, default=0)
    confidence = Column(Integer, default=0)
    
    # Hardened 2.0 Phase 7: Multi-persona approval (AIM-165)
    requires_senior_approval = Column(Boolean, default=False)
    senior_approver_id = Column(String, ForeignKey("users.id"), nullable=True)
    governance_notes = Column(Text, nullable=True)
    
    # Snapshot of campaign state (status, budget) BEFORE the change was applied
    original_state_snapshot = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class LandingPage(Base):
    """Sovereign conversion pages (AIM-109)."""

    __tablename__ = "landing_pages"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Structure: { "theme": "...", "sections": [{ "type": "hero", "content": {...} }, ...] }
    content_json = Column(JSON, nullable=False, default=dict)
    
    is_published = Column(String, default="false", server_default="false")
    views_count = Column(Integer, default=0)
    conversions_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class LeadForm(Base):
    """Custom lead capture forms (AIM-112)."""

    __tablename__ = "lead_forms"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String, nullable=False)
    # Schema: [{ "label": "Full Name", "type": "text", "required": true, "key": "full_name" }, ...]
    fields_json = Column(JSON, nullable=False, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
