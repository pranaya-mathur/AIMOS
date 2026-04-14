# AIMOS Feature Gap Analysis

This document maps the detailed AIMOS feature backlog to what is currently present in this repository.

It is based on:

- the current FastAPI + Celery + Next.js implementation
- the 12-agent orchestration layer already wired in code
- the detailed feature list covering AIM-001 through AIM-173

## Status legend

- `Implemented`: working code path exists in backend and/or frontend
- `Partial`: prompts, stubs, or supporting infrastructure exist, but the full product feature is not complete
- `Missing`: no meaningful implementation exists yet

## Current repo shape

The repo is strongest in these areas:

- campaign orchestration and async job execution
- agent prompt scaffolding for 12 major modules
- billing and quota enforcement
- launch integrations for Meta, Google, WhatsApp, email, SMS, and X
- analytics snapshots and optimization scheduling
- media generation plumbing and creative library UI

The repo is weakest in these areas:

- seller onboarding and setup flows
- structured business and brand data models
- persistent AI outputs beyond campaign payload blobs
- landing page and page-builder features
- admin console UX
- seller-facing configuration workflows for profiles, audiences, and products

## Module-level alignment

| Module | Feature IDs | Repo status | Notes |
|--------|-------------|-------------|-------|
| Smart Onboarding | AIM-001 to AIM-005 | `Missing` | No onboarding flow, no onboarding state, no seller profile model for business type, industry, goal, budget, or platform preference. |
| Brand Setup | AIM-006 to AIM-012 | `Missing` | No brand profile, product catalog, audience profile, pricing model, or business profile API. Current system jumps straight to campaign input. |
| AI Business Analyzer | AIM-014 to AIM-025 | `Partial` | Agent exists with prompt/schema support for competitor notes, audience hypotheses, platform and budget recommendations, but there is no dedicated analyzer workflow, no competitor data source, and no persisted analyzer domain model. |
| AI Brand Builder | AIM-026 to AIM-036 | `Partial` | Prompt/schema support exists for narrative, positioning, palette, typography, voice, and template suggestions. Real logo generation, downloadable brand kit, and template asset production are not implemented. |
| AI Content Studio | AIM-037 to AIM-055 | `Partial` | Media job infrastructure, creative library, and download paths exist. Full creative editor, AI background replacement, lifestyle mockups, video composition quality, and robust asset management remain incomplete. |
| AI Campaign Builder | AIM-056 to AIM-072 | `Partial` | Campaign creation, rerun, preview-like output, and launch integrations exist. True AI-generated campaign structures, audience object creation, lookalikes, budget distribution logic, and one-click end-to-end publishing are still incomplete. |
| AI Analytics Engine | AIM-073 to AIM-086 | `Partial` | Metrics storage, campaign analytics pages, and optimization hooks exist. Industry benchmarks, comparative analysis depth, alerts, forecasting, and richer dashboard insights are still limited or absent. |
| AI Optimization Engine | AIM-087 to AIM-098 | `Partial` | Scheduled optimization tick and optimization agent exist. Fully automated rules, budget shifts, fatigue detection, and self-learning optimization are not fully operational. |
| AI Growth Planner | AIM-099 to AIM-108 | `Partial` | Growth planner agent exists at prompt level. No dedicated workflow, planning UI, or persistent recommendation objects yet. |
| AI Lead Capture System | AIM-109 to AIM-122 | `Partial` | Lead model, WhatsApp webhook capture, and prompt-level lead strategy exist. Page builder, generated landing pages, form builder, CRM sync, and conversion tracking are not fully built. |
| AI Sales Agent | AIM-123 to AIM-133 | `Partial` | Sales agent prompt layer exists, and conversation records exist. Live chatbot deployment, qualification flows, booking, and calendar sync are not implemented. |
| AI Customer Engagement Engine | AIM-134 to AIM-145 | `Partial` | Email, SMS, and WhatsApp integration plumbing exists. Unified campaign builder, behavior-based triggers, segmentation workflows, and engagement analytics UI are not complete. |
| AI Business Dashboard | AIM-146 to AIM-152 | `Partial` | Dashboard shell and analytics pages exist. Widget customization, recommendation surfaces, and polished seller overview metrics remain incomplete. |
| Monetization | AIM-153 to AIM-159 | `Implemented` / `Partial` | Subscription plans, Stripe checkout, quotas, and usage enforcement are present. Add-ons and richer self-serve plan management are only partially present. |
| Integrations | AIM-160 to AIM-167 | `Partial` | Meta, Google, image, video, and voice integration paths exist at infrastructure level. Shopify, WooCommerce, and automation integrations are not yet built. |
| Admin Panel | AIM-168 to AIM-173 | `Partial` | Admin role and some admin/analytics endpoints exist. There is no complete admin-facing UI for user management, moderation, toggles, and system alerts. |

## Highest-priority gaps for MVP correctness

These are the most important missing foundations if the product should truly reflect the backlog rather than only the current campaign engine.

### 1. Seller profile foundation

Missing backlog:

- AIM-001 to AIM-005
- AIM-006
- AIM-008 to AIM-012

Why it matters:

- the whole AI system currently depends on ad hoc `campaign.input`
- there is no reusable seller context across campaigns
- the analyzer, brand builder, and campaign builder cannot build cumulative memory

Recommended implementation:

1. Add a `seller_profiles` table keyed to `users`
2. Add `brand_profiles`, `audience_profiles`, and `product_catalog_items`
3. Add onboarding APIs and a frontend onboarding wizard
4. Feed these objects into campaign creation and agent prompts

### 2. Persistent brand system

Missing backlog:

- AIM-007
- AIM-026 to AIM-032
- AIM-036

Why it matters:

- the repo can generate brand recommendations, but not a durable brand kit
- users cannot upload a logo, approve palette decisions, or reuse brand assets cleanly

Recommended implementation:

1. Add persistent brand asset storage and metadata
2. Add brand approval and edit flows in the frontend
3. Separate brand generation from campaign execution
4. Store approved brand kits for downstream content and campaign builders

### 3. True lead capture product

Missing backlog:

- AIM-109 to AIM-119

Why it matters:

- there is a lead table, but not a seller-facing conversion system
- current lead capture is integration-first rather than product-first

Recommended implementation:

1. Add landing page entities and publishing flow
2. Add form schemas and submission storage
3. Add source attribution and conversion event models
4. Connect captured leads to sales and engagement workflows

## Best-supported backlog areas today

If delivery needs to stay close to the current architecture, these are the safest near-term claims:

- AIM-153 to AIM-157: subscriptions, quota tracking, usage limits, alerts
- AIM-054 to AIM-055: asset download and creative storage
- AIM-073 to AIM-080: basic campaign metrics, creative metrics, and funnel-style analytics support
- AIM-087 baseline: scheduled optimization monitoring exists
- AIM-146 to AIM-150: business dashboard shell exists
- AIM-160 to AIM-164: core integration plumbing exists

## Recommended implementation order

To align the repo with the backlog while preserving the current architecture, build in this order:

1. `M1 foundation`
Add onboarding, seller profile, brand profile, audience profile, and product/service models.

2. `M1 guided setup`
Add frontend flows for AIM-001 to AIM-012 and persist outputs instead of burying them in campaign JSON.

3. `M1 analyzer productization`
Expose a dedicated Business Analyzer workflow that consumes seller profile data and saves structured outputs.

4. `M2 brand system`
Turn prompt-only brand output into a real brand kit with asset storage, approvals, and reuse.

5. `M2 lead capture and editor`
Build landing page/form features and complete the creative editor loop.

6. `M3 execution polish`
Deepen campaign publishing, analytics, and dashboard fidelity using the new structured data foundation.

## Suggested database additions

Minimum schema additions to unlock the backlog cleanly:

- `seller_profiles`
- `brand_profiles`
- `brand_assets`
- `audience_profiles`
- `products_or_services`
- `business_analysis_reports`
- `landing_pages`
- `lead_forms`
- `lead_events`
- `campaign_recommendations`

## Practical conclusion

This repo is not an empty start. It already provides a strong execution engine for campaigns, agents, billing, async work, and integrations.

But relative to the detailed feature sheet, it is still missing the product foundations that make AIMOS feel like a seller operating system instead of a campaign orchestration backend. The most important missing work is not another agent prompt. It is the data model and UX for onboarding, brand setup, seller context, and lead capture.
