
from fastapi import APIRouter
from celery.result import AsyncResult
from celery_app import celery

router = APIRouter()

@router.get("/{task_id}")
def status(task_id: str):
    task = AsyncResult(task_id, app=celery)
    return {"status": task.status, "result": task.result}
