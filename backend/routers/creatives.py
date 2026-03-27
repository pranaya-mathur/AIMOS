from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from deps import get_agency_user
from models import User
from tasks import generate_variation

router = APIRouter()


class VariationsBody(BaseModel):
    brief: str = Field(..., min_length=1, description="Campaign / creative brief")
    n: int = Field(default=3, ge=1, le=10, description="Number of parallel variations")


@router.post("/variations")
def creative_variations(
    body: VariationsBody,
    user: Optional[User] = Depends(get_agency_user),
):
    """Queues N parallel OpenAI creative copy tasks (Celery). Poll GET /job/{task_id} for each."""
    uid = user.id if user else None
    task_ids = []
    for i in range(body.n):
        task_ids.append(generate_variation.delay(body.brief, i, user_id=uid).id)
    return {"task_ids": task_ids, "count": body.n}
