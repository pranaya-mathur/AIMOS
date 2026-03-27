
from celery import Celery
from celery.schedules import crontab

from core.config import get_settings

settings = get_settings()

celery = Celery(
    "aimos",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks"],
)

celery.conf.timezone = "UTC"
celery.conf.beat_schedule = {
    "aimos-optimization-hourly": {
        "task": "tasks.optimization_tick",
        "schedule": crontab(minute=0),
    },
}
