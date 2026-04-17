
from celery import Celery
from celery.schedules import crontab

from core.config import get_settings

settings = get_settings()

celery = Celery(
    "aimos",
    broker=settings.redis_url,
    backend="cache+memory://localhost" if "memory" in settings.redis_url else settings.redis_url,
    include=["tasks"],
)

# 2.0 Standalone: Enable synchronous execution for local E2E validation
celery.conf.task_always_eager = True
celery.conf.task_eager_propagates = True

celery.conf.timezone = "UTC"
celery.conf.beat_schedule = {
    "aimos-optimization-hourly": {
        "task": "tasks.optimization_tick",
        "schedule": crontab(minute=0),
    },
}
