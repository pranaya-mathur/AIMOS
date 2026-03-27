import uuid
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import User
from services.auth import create_access_token, hash_password, verify_password

router = APIRouter()


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    role: Literal["agency_client", "end_customer"] = "agency_client"


class LoginBody(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    uid = str(uuid.uuid4())
    user = User(
        id=uid,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "role": user.role}


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "role": user.role}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }
