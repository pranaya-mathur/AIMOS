from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import get_db
from deps import get_admin_user
from models import User
from services.usage.quotas import usage_summary_for_user

router = APIRouter()

class UserSchema(BaseModel):
    id: str
    email: str
    role: str
    full_name: Optional[str] = None
    monthly_campaign_quota: Optional[int] = None
    monthly_token_quota: Optional[int] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    role: Optional[str] = None
    monthly_campaign_quota: Optional[int] = None
    monthly_token_quota: Optional[int] = None

@router.get("/users", response_model=List[UserSchema])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """List all users (paginated)."""
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/users/{user_id}")
def get_user_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Get detailed user profile + current monthly usage summary."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    summary = usage_summary_for_user(db, user)
    return {
        "profile": UserSchema.from_orm(user),
        "usage_summary": summary
    }

@router.patch("/users/{user_id}", response_model=UserSchema)
def update_user_admin(
    user_id: str,
    body: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Update user role or quota overrides."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if body.role is not None:
        user.role = body.role
    if body.monthly_campaign_quota is not None:
        user.monthly_campaign_quota = body.monthly_campaign_quota
    if body.monthly_token_quota is not None:
        user.monthly_token_quota = body.monthly_token_quota
    
    db.commit()
    db.refresh(user)
    return user
