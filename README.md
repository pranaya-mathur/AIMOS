# AIMOS Enterprise — AI Marketing Operating System

[![Enterprise-Ready](https://img.shields.io/badge/Status-Hardened_2.0_Verified-success?style=for-the-badge)](https://github.com/pranaya-mathur/AIMOS)
[![Architecture](https://img.shields.io/badge/Architecture-LangGraph_Multi_Agent-blue?style=for-the-badge)](docs/PRODUCT_ARCHITECTURE.md)
[![Tech Stack](https://img.shields.io/badge/Tech-FastAPI_React_PostgreSQL-blueviolet?style=for-the-badge)](package.json)
[![License](https://img.shields.io/badge/Scale-Enterprise_Ready-brightgreen?style=for-the-badge)](LICENSE)

**AIMOS Enterprise** is a full-stack AI-powered marketing operating system designed for agencies. It orchestrates a sophisticated multi-agent pipeline that transforms business objectives into revenue-generating outcomes across the entire marketing funnel—from competitive intelligence through autonomous optimization to AI-driven sales engagement.

**Status**: 85% production-ready. All core systems implemented, e-commerce integrations require credential injection for production deployment.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Core Capabilities](#core-capabilities)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Feature Modules](#feature-modules)
- [Integration Status](#integration-status)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)
- [Security & Compliance](#security--compliance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## 📌 Project Overview

AIMOS is built on the vision of automating the entire marketing lifecycle for agencies:

1. **Plan & Analyze**: Competitive intelligence, market analysis, and strategic planning
2. **Create & Optimize**: AI-generated creative assets and continuous campaign optimization
3. **Execute & Monitor**: Multi-channel campaign orchestration across Meta, Google, X (Twitter), and more
4. **Engage & Convert**: AI chatbots, landing pages, and multi-channel engagement (WhatsApp, Email, SMS)
5. **Learn & Iterate**: Persistent wisdom layer that learns from past campaigns

The system is designed as a **multi-tenant, agency-ready platform** with enterprise-grade governance, RBAC, and audit logging.

---

## 🏛️ Core Capabilities

### 1. Strategic Intelligence & Memory 2.0
- **Competitor Spy Agent**: Real-time ad intelligence and market grounding for every campaign decision
- **Brand Wisdom Layer**: Persistent learning across campaigns—AIMOS remembers winning hooks, audience segments, and creative themes
- **Unified Seller Profile**: Deep context persistence for D2C, SaaS, Creator, and Local Business brands
- **Market Analysis**: Automated competitive landscape analysis and opportunity identification

### 2. Autonomous Autopilot & Financial Safety
- **Governance-Safe Optimization**: Autonomous budget shifts and creative rotations with mandatory **5-minute human-in-the-loop undo window**
- **Financial Hard Caps**: Per-organization "Autopilot Constraint" policies to prevent runaway spending
- **Inventory Guard**: Real-time sync with Shopify & WooCommerce; automatically pauses ads for out-of-stock items
- **Budget Orchestration**: Intelligent budget allocation across campaigns based on performance metrics

### 3. Full-Funnel Conversion Engines
- **AI Landing Page Generator**: High-fidelity, conversion-optimized landing pages generated in seconds
- **Form Auto-Validation**: Dynamic form generation with real-time validation
- **Sales Intelligence Chatbot**: Context-aware qualification agents that capture leads, score intent, and handle FAQs 24/7
- **Multi-Channel Engagement**: Automated lead nurturing via WhatsApp, Email, and SMS

### 4. Enterprise Governance & Admin
- **Multi-Tenant Architecture**: Rigid data isolation and RBAC for multi-tenant agency management
- **Organization-Level Controls**: Whitelabeling support, seat quotas, and orchestration controls
- **Multi-Persona Approval**: High-risk budget directives require co-signing from senior stakeholders
- **Portfolio Command Tower**: Aggregated performance monitoring (Spend, ROAS, Revenue) across brand portfolios
- **Immutable Audit Trail**: Every optimization, budget shift, and user action is logged

---

## 🏗️ Architecture

### System Architecture

AIMOS is a distributed system with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│           ┌──────────────────────────────────────┐              │
│           │  - Agency Command Center             │              │
│           │  - Campaign Dashboard                │              │
│           │  - Landing Page Builder              │              │
│           │  - Performance Analytics              │              │
│           │  - Admin & Team Management           │              │
│           └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                          ↕ REST API
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Core Modules (23 routers)                               │   │
│  │  - auth.py        → JWT auth, login, registration       │   │
│  │  - org.py         → Organization management              │   │
│  │  - campaign.py    → Campaign CRUD and orchestration      │   │
│  │  - agents.py      → Agent provisioning & control         │   │
│  │  - orchestration.py → Multi-agent coordination           │   │
│  │  - landing_pages.py → Landing page generation            │   │
│  │  - chat.py        → Sales chatbot endpoints              │   │
│  │  - analytics.py   → Performance metrics & reporting      │   │
│  │  - leads.py       → Lead capture and qualification       │   │
│  │  - media.py       → Creative asset management            │   │
│  │  - creatives.py   → Creative generation & optimization   │   │
│  │  - webhooks.py    → External platform webhooks           │   │
│  │  - billing.py     → Stripe integration & subscriptions   │   │
│  │  - usage.py       → Usage tracking & quotas              │   │
│  │  - admin.py       → Admin panel endpoints                │   │
│  │  - health.py      → System health & readiness checks     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LangGraph Orchestrator (services/orchestrator.py)       │   │
│  │  - Multi-agent coordination                              │   │
│  │  - Agentic workflow execution                            │   │
│  │  - State management & persistence                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Integration Services                                     │   │
│  │  - openai_service.py       → OpenAI LLM calls            │   │
│  │  - stability_ai.py         → Image generation            │   │
│  │  - meta_marketing.py       → Meta Ads API               │   │
│  │  - google_ads.py           → Google Ads API             │   │
│  │  - social_x.py             → Twitter/X API              │   │
│  │  - whatsapp_cloud.py       → WhatsApp Cloud API         │   │
│  │  - engagement_email.py     → SendGrid integration        │   │
│  │  - engagement_sms.py       → Twilio integration          │   │
│  │  - media_clients.py        → Creative APIs               │   │
│  │  - ecom_service.py         → Shopify/WooCommerce sync    │   │
│  │  - webhook_security.py     → Webhook validation          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Database & Auth                                          │   │
│  │  - SQLAlchemy ORM models (20+ tables)                     │   │
│  │  - JWT token management                                   │   │
│  │  - Password hashing with bcrypt                           │   │
│  │  - RBAC & organization silos                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          ↕ Async Tasks
┌─────────────────────────────────────────────────────────────────┐
│                    Celery Worker Layer                           │
│  - Background job processing                                     │
│  - Media generation tasks                                        │
│  - Inventory sync jobs                                           │
│  - Email/SMS dispatch                                            │
│  - Webhook event handling                                        │
└─────────────────────────────────────────────────────────────────┘
                          ↕ Caching
┌─────────────────────────────────────────────────────────────────┐
│                      Redis Cache                                 │
│  - Session management                                            │
│  - Task queue                                                    │
│  - Real-time data caching                                        │
└─────────────────────────────────────────────────────────────────┘
                          ↕ Storage
┌─────────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                            │
│  - Organizations, Users, Teams                                   │
│  - Campaigns, Brands, Ads                                        │
│  - Leads, Analytics, Audit Logs                                  │
│  - JSONB for flexible agent memories                             │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Request
    ↓
FastAPI Router (auth, campaign, etc.)
    ↓
Service Layer (business logic)
    ↓
LangGraph Orchestrator (multi-agent coordination)
    ↓
Integration Services (OpenAI, Meta, Google, etc.)
    ↓
External APIs & Platforms
    ↓
Webhook Events → Celery Workers → Database Updates
    ↓
Response → Frontend
```

---

## 📂 Project Structure

```
AIMOS/
├── backend/                          # FastAPI application
│   ├── main.py                      # Application entry point
│   ├── db.py                        # SQLAlchemy setup & migrations
│   ├── models.py                    # ORM models (Organizations, Users, Campaigns, etc.)
│   ├── celery_app.py                # Celery task queue setup
│   ├── core/
│   │   ├── config.py                # Environment configuration
│   │   └── logging_config.py        # Logging setup
│   ├── routers/                     # API endpoint handlers (23 routers)
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── org.py                   # Organization management
│   │   ├── campaign.py              # Campaign CRUD & orchestration
│   │   ├── agents.py                # AI agent provisioning
│   │   ├── orchestration.py         # Multi-agent workflows
│   │   ├── landing_pages.py         # Landing page generation
│   │   ├── chat.py                  # Chatbot endpoints
│   │   ├── analytics.py             # Performance metrics
│   │   ├── leads.py                 # Lead capture & qualification
│   │   ├── media.py                 # Media asset management
│   │   ├── creatives.py             # Creative generation
│   │   ├── webhooks.py              # External webhooks
│   │   ├── billing.py               # Stripe integration
│   │   ├── usage.py                 # Usage tracking
│   │   ├── admin.py                 # Admin panel
│   │   ├── health.py                # Health checks
│   │   └── ...                      # 8 more routers
│   ├── services/
│   │   ├── orchestrator.py          # LangGraph multi-agent coordinator
│   │   ├── auth/
│   │   │   ├── tokens.py            # JWT token management
│   │   │   └── passwords.py         # Password hashing & validation
│   │   └── integrations/
│   │       ├── openai_service.py    # OpenAI LLM integration
│   │       ├── stability_ai.py      # Image generation
│   │       ├── meta_marketing.py    # Meta Ads API
│   │       ├── google_ads.py        # Google Ads API
│   │       ├── social_x.py          # Twitter/X API
│   │       ├── whatsapp_cloud.py    # WhatsApp Cloud API
│   │       ├── engagement_email.py  # SendGrid integration
│   │       ├── engagement_sms.py    # Twilio integration
│   │       ├── media_clients.py     # Creative generation APIs
│   │       ├── ecom_service.py      # Shopify/WooCommerce sync
│   │       ├── webhook_security.py  # Webhook validation
│   │       └── ...                  # Additional services
│   ├── tasks.py                     # Celery task definitions
│   ├── migrations/                  # Alembic database migrations
│   ├── scripts/
│   │   ├── db_init.py               # Database initialization
│   │   ├── master_e2e_validation.py # End-to-end validation
│   │   └── ...                      # Verification & validation scripts
│   └── requirements.txt             # Python dependencies
│
├── frontend/                        # Next.js 16 application
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── login/                   # Authentication pages
│   │   └── (shell)/                 # Main dashboard shell with 19+ pages
│   │       ├── campaigns/           # Campaign management
│   │       ├── analytics/           # Performance dashboards
│   │       ├── leads/               # Lead management
│   │       ├── chat/                # Sales chatbot interface
│   │       ├── landing-pages/       # Landing page builder
│   │       ├── creatives/           # Asset library
│   │       ├── agents/              # Agent management
│   │       ├── organization/        # Org settings
│   │       ├── team/                # Team management
│   │       ├── billing/             # Subscription management
│   │       └── ...                  # Additional pages
│   ├── components/                  # Reusable React components
│   ├── hooks/                       # Custom React hooks
│   ├── lib/                         # Utilities & helpers
│   ├── public/                      # Static assets
│   ├── package.json                 # Node.js dependencies
│   └── tsconfig.json                # TypeScript configuration
│
├── docs/                            # Project documentation
│   ├── PRODUCT_ARCHITECTURE.md      # Detailed architecture docs
│   ├── BUBBLE_INTEGRATION_GUIDE.md  # No-code platform integration
│   ├── PROMPT_CUSTOMIZATION.md      # AI agent prompt configuration
│   ├── E2E_TESTING.md               # Test strategy & examples
│   ├── FEATURE_GAP_ANALYSIS.md      # Feature roadmap
│   └── bubble/                      # Bubble.io integration files
│
├── prompts/                         # AI agent prompt templates
│   └── *.yaml                       # Agentic workflow prompts
│
├── scripts/                         # Utility & deployment scripts
│   ├── validate_env.py              # Environment validation
│   ├── master_e2e_validation.py     # System health check
│   └── ...                          # Additional scripts
│
├── tests/                           # Test suite
│   ├── test_*.py                    # Unit & integration tests
│   └── e2e/                         # End-to-end test scenarios
│
├── infra/                           # Infrastructure as Code
│   └── ...                          # Kubernetes manifests, Terraform, etc.
│
├── docker-compose.yml               # Local development compose
├── Dockerfile                       # API container definition
├── package.json                     # Monorepo root package
├── setup.sh                         # One-command bootstrap script
├── Makefile                         # Development tasks
├── .env.example                     # Environment template
├── API_FEASIBILITY_REPORT.md        # Integration readiness status
└── README.md                        # This file
```

---

## 🛠️ Tech Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.100+ | High-performance REST API with async support |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction layer with support for complex queries |
| **Database** | PostgreSQL | 15+ | Primary data storage with JSONB for flexible agent memories |
| **Cache** | Redis | 7+ | Session management, caching, and task queue |
| **Task Queue** | Celery | 5.3+ | Asynchronous task processing for long-running operations |
| **LLM Orchestration** | LangGraph | Latest | Multi-agent coordination and agentic workflow orchestration |
| **AI/LLM** | OpenAI API | GPT-4 | Primary LLM for agent reasoning and creative generation |
| **Image Gen** | Stability AI | Latest | Image generation for creative assets |
| **Auth** | PyJWT + bcrypt | Latest | JWT token management and password hashing |
| **Error Tracking** | Sentry | Latest | Production error monitoring |
| **Rate Limiting** | SlowAPI | Latest | API rate limiting and quota enforcement |
| **Validation** | Pydantic | 2.0+ | Data validation and settings management |
| **Migration** | Alembic | Latest | Database schema versioning |
| **Testing** | Pytest + pytest-asyncio | Latest | Unit and integration testing framework |
| **Load Testing** | Locust | Latest | Performance and stress testing |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Next.js | 16.2+ | React meta-framework with SSR & static generation |
| **UI Library** | React | 19+ | Component-based UI development |
| **Styling** | Tailwind CSS | 4+ | Utility-first CSS framework |
| **UI Components** | Radix UI | Latest | Accessible, unstyled component library |
| **Data Fetching** | TanStack Query | 5.99+ | Server state management and caching |
| **Animations** | Framer Motion | 12+ | Smooth UI animations and transitions |
| **Charts** | Recharts | 3.8+ | Data visualization and dashboards |
| **Icons** | Lucide React | 1.8+ | SVG icon library |
| **Type Safety** | TypeScript | 5+ | Static type checking |
| **Linting** | ESLint | 9+ | Code quality and consistency |
| **API Generation** | OpenAPI TypeScript | 7.13+ | Auto-generated type-safe API client |

### Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | API container image for deployment |
| **Orchestration** | docker-compose | Local development environment |
| **Secrets Management** | Environment variables | Configuration management |
| **CI/CD** | (Project-ready) | Ready for GitHub Actions, GitLab CI, or Jenkins |
| **Deployment** | AWS Fargate | Serverless container orchestration |

### External Integrations
| Service | Purpose | Status |
|---------|---------|--------|
| **OpenAI** | LLM inference & embeddings | ✅ Production Ready |
| **Stability AI** | Image generation | ✅ Production Ready |
| **Meta Ads API** | Facebook/Instagram ad campaigns | ✅ Production Ready |
| **Google Ads API** | Google Ads campaign management | ✅ Production Ready |
| **X (Twitter) API** | Social media automation | ✅ Production Ready |
| **WhatsApp Cloud API** | Messaging and lead engagement | ✅ Production Ready |
| **SendGrid** | Email delivery | ✅ Production Ready |
| **Twilio** | SMS communications | ✅ Production Ready |
| **Stripe** | Payment processing & subscriptions | ✅ Production Ready |
| **Shopify API** | E-commerce inventory sync | ⚠️ Prototype (mock responses) |
| **WooCommerce API** | E-commerce inventory sync | ⚠️ Placeholder |
| **AdCreative.ai** | Creative variation generation | ✅ Production Ready |
| **Pictory.ai** | Video content generation | ✅ Production Ready |
| **ElevenLabs** | Audio/voice generation | ✅ Production Ready |

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** with npm
- **Docker & Docker Compose** (for local development)
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/pranaya-mathur/AIMOS.git
cd AIMOS
```

### Step 2: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Required environment variables:
# - OPENAI_API_KEY         # Your OpenAI API key
# - STABILITY_API_KEY      # Stability AI API key
# - META_ACCESS_TOKEN      # Meta Ads API access token
# - GOOGLE_ADS_DEVELOPER_TOKEN  # Google Ads developer token
# - JWT_SECRET             # Secret key for JWT token signing
# - DATABASE_URL           # PostgreSQL connection string
# - REDIS_URL              # Redis connection string
# - STRIPE_SECRET_KEY      # Stripe API secret
# - STRIPE_PUBLISHABLE_KEY # Stripe public key
```

### Step 3: Bootstrap the Application

```bash
# One-command setup: validates environment, builds containers, and seeds the database
./setup.sh
```

This script will:
- ✅ Validate all required environment variables
- ✅ Build Docker containers
- ✅ Start PostgreSQL, Redis, API, worker, and beat services
- ✅ Initialize the database schema
- ✅ Create a development user

### Step 4: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health/ready

# View API documentation
open http://localhost:8000/docs

# Run the end-to-end validation suite
python3 scripts/master_e2e_validation.py
```

### Development Credentials

After setup, you can log in with:
- **Email**: `aimos-dev@example.com`
- **Password**: `devpass123`

---

## 📚 API Documentation

### Interactive API Docs
Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Structure

The AIMOS API is organized into logical modules:

#### Authentication
```
POST   /auth/login                 # User login
POST   /auth/logout                # User logout
POST   /auth/register              # User registration
POST   /auth/refresh-token         # Refresh JWT token
```

#### Organizations
```
GET    /orgs                       # List organizations
POST   /orgs                       # Create organization
GET    /orgs/{org_id}              # Get organization details
PUT    /orgs/{org_id}              # Update organization
DELETE /orgs/{org_id}              # Delete organization
```

#### Campaigns
```
GET    /campaigns                  # List campaigns
POST   /campaigns                  # Create campaign
GET    /campaigns/{campaign_id}    # Get campaign details
PUT    /campaigns/{campaign_id}    # Update campaign
DELETE /campaigns/{campaign_id}    # Delete campaign
POST   /campaigns/{campaign_id}/launch  # Launch campaign
POST   /campaigns/{campaign_id}/pause   # Pause campaign
```

#### Agents
```
GET    /agents                     # List available agents
POST   /agents/provision           # Provision new agent
GET    /agents/{agent_id}          # Get agent details
POST   /agents/{agent_id}/execute  # Execute agent
```

#### Landing Pages
```
POST   /landing-pages              # Generate landing page
GET    /landing-pages/{page_id}    # Get landing page
PUT    /landing-pages/{page_id}    # Update landing page
POST   /landing-pages/{page_id}/publish  # Publish page
```

#### Analytics
```
GET    /analytics/campaigns        # Campaign performance metrics
GET    /analytics/leads            # Lead analytics
GET    /analytics/spend            # Spend analysis
GET    /analytics/roas             # ROAS metrics
```

#### Leads
```
GET    /leads                      # List leads
POST   /leads/capture              # Capture new lead
PUT    /leads/{lead_id}            # Update lead
GET    /leads/{lead_id}/score      # Get lead qualification score
```

#### Webhooks
```
POST   /webhooks/meta              # Meta Ads webhooks
POST   /webhooks/google            # Google Ads webhooks
POST   /webhooks/stripe            # Stripe payment webhooks
```

---

## 🧩 Feature Modules

### 1. Campaign Management Module
**Location**: `backend/routers/campaign.py`, `backend/services/orchestrator.py`

Capabilities:
- Campaign creation with multi-channel support (Meta, Google Ads, X)
- AI-powered campaign optimization
- A/B testing setup and management
- Real-time performance monitoring
- Autonomous budget allocation

### 2. AI Agent System (LangGraph)
**Location**: `backend/services/orchestrator.py`, `backend/routers/agents.py`

Agents Included:
- **Competitor Spy**: Analyzes competitor ads and market trends
- **Wisdom Extractor**: Learns from historical campaign data
- **Autopilot Optimizer**: Autonomous campaign optimization with human oversight
- **Creative Director**: Generates and optimizes creative assets
- **Sales Qualification Agent**: Scores and qualifies leads

### 3. Creative Generation Module
**Location**: `backend/routers/creatives.py`, `backend/services/integrations/media_clients.py`

Capabilities:
- Image generation (Stability AI)
- Video generation (Pictory.ai)
- Ad creative variations (AdCreative.ai)
- Audio generation (ElevenLabs)
- Brand asset management and versioning

### 4. Landing Page Builder
**Location**: `backend/routers/landing_pages.py`

Capabilities:
- AI-powered landing page generation
- Conversion-optimized templates
- Dynamic form generation with validation
- A/B testing support
- Real-time preview and publishing

### 5. Sales Intelligence Chatbot
**Location**: `backend/routers/chat.py`

Capabilities:
- Lead qualification through conversation
- Intent scoring and analysis
- 24/7 availability with context awareness
- Multi-turn conversation support
- Seamless lead handoff to CRM

### 6. E-Commerce Integration
**Location**: `backend/services/integrations/ecom_service.py`

Capabilities:
- Real-time inventory sync with Shopify/WooCommerce
- Automatic ad pausing for out-of-stock items
- Product catalog management
- SKU tracking and updates

### 7. Multi-Channel Engagement
**Location**: `backend/routers/leads.py`, `backend/services/integrations/`

Channels:
- **WhatsApp**: Direct messaging and lead nurturing
- **Email**: SendGrid integration for email campaigns
- **SMS**: Twilio integration for text notifications

### 8. Analytics & Reporting
**Location**: `backend/routers/analytics.py`, `backend/routers/org_analytics.py`

Metrics Tracked:
- Campaign spend and ROI
- Lead generation and qualification rates
- Conversion rates and revenue attribution
- Creative performance and engagement metrics
- Team performance and productivity

### 9. Billing & Usage Management
**Location**: `backend/routers/billing.py`, `backend/routers/usage.py`

Features:
- Stripe subscription management
- Credit-based usage tracking
- Per-tier rate limiting
- Organization-level quotas
- Invoice generation

### 10. Team & Organization Management
**Location**: `backend/routers/org.py`, `backend/routers/team.py`

Features:
- Multi-tenant organization support
- RBAC (Role-Based Access Control)
- Team member management
- Approval workflows for high-risk actions
- Organization-level settings and whitelabeling

---

## 📊 Integration Status

### ✅ Production Ready (Implement with API Keys)

| Category | Service | Status | Notes |
|----------|---------|--------|-------|
| **LLM** | OpenAI (GPT-4, GPT-4o, Embeddings) | ✅ | Fully implemented, requires API key |
| **Image Gen** | Stability AI | ✅ | Integrated, requires API key |
| **Ads** | Meta Ads API | ✅ | Full Graph API implementation |
| **Ads** | Google Ads | ✅ | Campaign management ready |
| **Social** | X (Twitter) / Tweepy | ✅ | Tweet automation ready |
| **Messaging** | WhatsApp Cloud API | ✅ | Message templates & webhooks configured |
| **Email** | SendGrid | ✅ | Email delivery and tracking ready |
| **SMS** | Twilio | ✅ | SMS campaigns ready |
| **Payments** | Stripe | ✅ | Checkout & subscriptions fully implemented |
| **Creative** | AdCreative.ai | ✅ | Variation generation ready |
| **Creative** | Pictory.ai | ✅ | Video generation ready |
| **Creative** | ElevenLabs | ✅ | Voice/audio generation ready |

### ⚠️ Prototype / Mock Implementation

| Service | Status | Notes |
|---------|--------|-------|
| **Shopify** | ⚠️ Prototype | Using mock responses; ready for production credential injection |
| **WooCommerce** | ⚠️ Placeholder | Requires implementation with API keys |

### 🔄 Coming Soon

- Advanced audience segmentation
- Predictive analytics
- Multi-currency support
- Advanced compliance features

---

## 🔨 Development Workflow

### Running the Application

#### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

#### Services Started
- **API**: http://localhost:8000 (FastAPI + Uvicorn)
- **Database**: PostgreSQL at localhost:5433
- **Redis**: Redis at localhost:6380
- **Celery Worker**: Background job processing
- **Celery Beat**: Scheduled tasks

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Open in browser
open http://localhost:3000
```

### Backend Development

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run API directly (without Docker)
cd backend
uvicorn main:app --reload

# Run tests
pytest tests/ -v

# Run linting
pylint backend/ --disable=all --enable=E,F

# Type checking
mypy backend/
```

### Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Environment Variables

Key environment variables:
```bash
# Core
ENVIRONMENT=development|production
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Database
DATABASE_URL=postgresql://user:password@localhost:5433/aimos
REDIS_URL=redis://localhost:6380/0

# API Keys (Required)
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=sk-...
META_ACCESS_TOKEN=EAAB...
GOOGLE_ADS_DEVELOPER_TOKEN=...

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```

---

## 🚢 Deployment

### Prerequisites
- AWS account (or alternative cloud provider)
- Docker registry (ECR, Docker Hub, etc.)
- PostgreSQL database (managed or self-hosted)
- Redis instance

### Production Deployment

#### Option 1: AWS Fargate (Recommended)
```bash
# Build and push Docker image
docker build -t aimos-api:latest .
docker tag aimos-api:latest your-ecr-uri/aimos-api:latest
docker push your-ecr-uri/aimos-api:latest

# Deploy using CloudFormation or Terraform
# (See infra/ directory for infrastructure-as-code templates)
```

#### Option 2: Kubernetes
```bash
# Apply Kubernetes manifests (if available in infra/)
kubectl apply -f infra/k8s/

# Verify deployment
kubectl get pods -n aimos
kubectl logs -f deployment/aimos-api -n aimos
```

### Environment Setup
```bash
# Create production .env file
ENVIRONMENT=production
DATABASE_URL=<managed postgres url>
REDIS_URL=<managed redis url>
OPENAI_API_KEY=<your key>
# ... add other required keys
```

### Database Migrations in Production
```bash
# Run migrations before deployment
python backend/scripts/db_init.py
alembic upgrade head
```

### Monitoring & Logging
- **Error Tracking**: Sentry (configure SENTRY_DSN)
- **Logs**: CloudWatch (for AWS deployment)
- **Metrics**: Application Performance Monitoring (APM)
- **Health Checks**: `/health/ready` and `/health/live` endpoints

---

## 🛡️ Security & Compliance

### Architecture-Level Security

1. **Multi-Tenant Data Isolation**
   - All queries filtered by `organization_id`
   - Organization-level silos enforced at database and API layers
   - Cross-org data access is prevented

2. **Authentication & Authorization**
   - JWT token-based authentication
   - Bcrypt password hashing (cost factor: 12+)
   - Role-Based Access Control (RBAC) with roles: admin, manager, user
   - Token expiration: 24 hours (configurable)
   - Refresh token rotation

3. **API Security**
   - CORS middleware configuration
   - HTTPS/TLS enforcement
   - Rate limiting via SlowAPI (prevents abuse)
   - Request validation via Pydantic models
   - CSRF protection on state-changing operations

4. **Audit Logging**
   - Every financial action logged to immutable audit trail
   - Campaign changes tracked with timestamps and user attribution
   - Webhook events logged for compliance

5. **Data Protection**
   - PostgreSQL encryption at rest (configurable)
   - TLS for all external API communications
   - Sensitive data never logged (API keys, tokens)
   - JSONB columns for flexible data storage

6. **Financial Controls**
   - Autonomous autopilot with hard caps per organization
   - 5-minute human-in-the-loop undo window
   - Multi-person approval for large budget shifts (configurable threshold)
   - Per-organization spending limits

7. **Webhook Security**
   - HMAC signature verification for all incoming webhooks
   - Webhook event replay protection
   - Rate limiting on webhook endpoints

8. **Compliance Features**
   - GDPR-ready (user data export, deletion)
   - SOC 2 logging capabilities
   - Audit trail for compliance reporting
   - Data retention policies (configurable)

### Security Best Practices

✅ **Do's:**
- Keep `.env` file private and never commit it
- Rotate API keys regularly
- Use strong JWT_SECRET in production (minimum 32 characters)
- Enable HTTPS in production
- Monitor audit logs for suspicious activity
- Implement rate limiting on critical endpoints
- Use managed databases with automated backups

❌ **Don'ts:**
- Never expose API keys in logs or error messages
- Don't share sensitive data across organizations
- Don't disable authentication for debugging
- Don't run production without HTTPS
- Don't use development secrets in production
- Don't commit `.env` files to version control

---

## 🗺️ Roadmap

### Phase 1: Foundation (Current - ✅ Complete)
- [x] Multi-agent LangGraph orchestration
- [x] Core integrations (OpenAI, Stability AI, Meta, Google Ads)
- [x] Campaign management and optimization
- [x] Landing page generation
- [x] Lead capture and qualification
- [x] Multi-channel engagement (WhatsApp, Email, SMS)
- [x] Billing and usage management
- [x] RBAC and multi-tenancy

### Phase 2: Production Hardening (🔄 In Progress)
- [ ] E-commerce integration completion (Shopify/WooCommerce production)
- [ ] Advanced analytics dashboard
- [ ] AI-powered performance predictions
- [ ] Enhanced approval workflows
- [ ] Whitelabeling improvements
- [ ] Performance optimizations

### Phase 3: Advanced Features (📅 Planned)
- [ ] Predictive lead scoring
- [ ] Multivariate testing engine
- [ ] Advanced audience segmentation
- [ ] Real-time bidding optimization
- [ ] Competitor intelligence dashboards
- [ ] Custom report builder

### Phase 4: Enterprise Scale (🚀 Future)
- [ ] Multi-currency support
- [ ] Advanced compliance features
- [ ] Marketplace for third-party integrations
- [ ] White-label platform
- [ ] Custom agent builder
- [ ] Advanced data warehousing

See detailed feature gaps in: [FEATURE_GAP_ANALYSIS.md](docs/FEATURE_GAP_ANALYSIS.md)

---

## 🧪 Testing

### Test Structure
```
tests/
├── unit/                 # Unit tests for services
├── integration/          # Integration tests for API endpoints
├── e2e/                  # End-to-end workflow tests
└── conftest.py          # Pytest fixtures and configuration
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_auth.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run end-to-end tests only
pytest tests/e2e/ -v

# Run specific test
pytest tests/unit/test_campaign.py::test_create_campaign -v
```

### Test Examples

**Unit Test Example**:
```python
def test_password_hashing():
    from services.auth.passwords import hash_password, verify_password
    hashed = hash_password("securepass123")
    assert verify_password("securepass123", hashed)
    assert not verify_password("wrongpass", hashed)
```

**Integration Test Example**:
```python
@pytest.mark.asyncio
async def test_campaign_creation(client, headers):
    response = await client.post(
        "/campaigns",
        json={"name": "Test Campaign", "budget": 1000},
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["id"]
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/AIMOS.git
cd AIMOS
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-amazing-feature
```

### 3. Make Changes
- Follow the existing code style
- Add tests for new features
- Update documentation if needed
- Ensure all tests pass

### 4. Commit with Co-Author
```bash
git commit -m "Add amazing feature

- Detailed description of changes
- Any breaking changes or migrations needed

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### 5. Push and Open Pull Request
```bash
git push origin feature/your-amazing-feature
```

### Contribution Areas
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🧪 Test coverage
- 🚀 Performance optimizations
- 🔐 Security improvements

### Code Quality Standards
- All new features require tests
- Code must pass linting (ESLint for frontend, Pylint for backend)
- Documentation must be updated
- Commits should be atomic and well-described

---

## 📞 Support & Resources

### Documentation
- [Product Architecture](docs/PRODUCT_ARCHITECTURE.md) - Deep dive into system design
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger docs
- [Bubble.io Integration](docs/BUBBLE_INTEGRATION_GUIDE.md) - No-code integration guide
- [Prompt Customization](docs/PROMPT_CUSTOMIZATION.md) - Customizing AI agent behavior
- [E2E Testing](docs/E2E_TESTING.md) - Testing strategies and examples

### Common Issues

**Issue: API won't start**
```bash
# Check environment variables
env | grep -E "OPENAI|DATABASE|JWT"

# Check database connection
docker-compose logs db

# Rebuild containers
docker-compose down && docker-compose up --build
```

**Issue: Database migrations failing**
```bash
# Check migration status
alembic current

# Manually apply migrations
cd backend && alembic upgrade head

# Rollback and retry
alembic downgrade base && alembic upgrade head
```

**Issue: Webhook events not processing**
```bash
# Check Celery worker logs
docker-compose logs worker

# Verify Redis is running
redis-cli -p 6380 ping

# Check webhook event queue
docker-compose exec redis redis-cli -n 0 LLEN celery
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

AIMOS is built with:
- **LangGraph** for multi-agent orchestration
- **FastAPI** for high-performance APIs
- **Next.js** for modern frontend
- **PostgreSQL** for reliable data storage
- The open-source community for countless libraries and tools

---

## 📈 Getting Help

- **Issues**: GitHub Issues for bugs and feature requests
- **Documentation**: Check [docs/](docs/) for detailed guides
- **Community**: Connect with other AIMOS users

---

**Last Updated**: May 2026 | **Status**: 🟢 Active Development | **Maturity**: Enterprise-Ready (85%)

© 2026 AIMOS Enterprise. Optimized for AWS Fargate & Agency-Scale Deployment.
