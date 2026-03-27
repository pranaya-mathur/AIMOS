from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import User
from services.usage.quotas import usage_summary_for_user

router = APIRouter()


@router.get("/me")
def my_usage(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Monthly campaign + OpenAI token usage, estimated cost, and effective quota limits."""
    return usage_summary_for_user(db, user)
