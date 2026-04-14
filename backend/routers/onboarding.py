from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from deps import get_agency_user
from models import User

router = APIRouter()


@router.post("/complete")
def complete_onboarding(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Mark the user as having completed the onboarding flow."""
    if user is None:
        raise HTTPException(status_code=400, detail="User context required to complete onboarding")
    
    user_row = db.query(User).filter(User.id == user.id).first()
    if not user_row:
         raise HTTPException(status_code=404, detail="User not found")
    
    user_row.is_onboarded = "true"
    db.commit()
    return {"status": "success", "is_onboarded": True}


@router.get("/status")
def get_onboarding_status(
    user: Optional[User] = Depends(get_agency_user),
):
    """Check if the user has completed onboarding."""
    if user is None:
        return {"is_onboarded": True} # Local dev/auth disabled
    
    return {"is_onboarded": user.is_onboarded == "true"}
