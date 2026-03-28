
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from core.config import get_settings
from core.logging_config import configure_logging
from db import Base, apply_schema_patches, engine
import models  # noqa: F401  — register ORM models for metadata.create_all
from openapi_tags import OPENAPI_TAGS
from routers import admin, agents, auth, billing, campaign, creatives, health, job, launch, media, usage, webhooks

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    Base.metadata.create_all(bind=engine)
    apply_schema_patches()
    logger.info("application_startup complete")
    yield


app = FastAPI(
    title="AIMOS API",
    description=(
        "AI Marketing Operating System — REST API for Bubble.io or any HTTP client. "
        "Obtain a JWT via `POST /auth/login`, then send `Authorization: Bearer <token>`. "
        "Import OpenAPI from `/openapi.json` into Bubble API Connector."
    ),
    version="1.0.0",
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

_settings = get_settings()
if _settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )
    base = get_settings().public_api_base_url
    if base:
        openapi_schema["servers"] = [
            {"url": base.rstrip("/"), "description": "Public API base URL (Bubble / production)"},
        ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.openapi_url = "/openapi.json"
app.docs_url = "/docs"
app.redoc_url = "/redoc"

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(campaign.router, prefix="/campaign", tags=["campaign"])
app.include_router(job.router, prefix="/job", tags=["job"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(launch.router, prefix="/launch", tags=["launch"])
app.include_router(creatives.router, prefix="/creatives", tags=["creatives"])
app.include_router(media.router, prefix="/media", tags=["media"])
app.include_router(usage.router, prefix="/usage", tags=["usage"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/")
def root():
    return {"status": "running", "docs": "/docs", "openapi": "/openapi.json"}
