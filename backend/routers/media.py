from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from deps import get_agency_user
from models import MediaAsset, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MediaAssetSchema(BaseModel):
    id: str
    provider: str
    asset_type: str
    url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/assets", response_model=List[MediaAssetSchema])
def get_media_assets(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Fetch all AI-generated assets for the current user/organization."""
    query = db.query(MediaAsset)
    
    if user:
        if user.organization_id:
            query = query.filter(MediaAsset.user_id.in_(
                db.query(User.id).filter(User.organization_id == user.organization_id)
            ))
        else:
            query = query.filter(MediaAsset.user_id == user.id)
    
    return query.order_by(MediaAsset.created_at.desc()).all()

@router.delete("/assets/{asset_id}")
def delete_media_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Delete a generated asset from the library."""
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    # Check ownership
    if user:
        if user.organization_id:
            # Check if asset owner is in same org
            owner = db.query(User).filter(User.id == asset.user_id).first()
            if not owner or owner.organization_id != user.organization_id:
                if user.role != "platform_admin":
                    raise HTTPException(status_code=403, detail="Forbidden")
        elif asset.user_id != user.id:
            if user.role != "platform_admin":
                raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(asset)
    db.commit()
    return {"ok": True}
