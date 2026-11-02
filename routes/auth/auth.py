
import os
import bcrypt
import jwt
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException,Depends
from database import get_db
from sqlalchemy.orm import Session
from routes.admin.admin_model import Admin
from routes.auth.Schema import LoginRequest, LoginResponse


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing")

router = APIRouter(tags=["Auth"])



@router.post("/login")
def login(data: LoginRequest, db:Session=Depends(get_db)):
   
    email=str(data.email).lower()
    admin=(
        db.query(Admin)
        .filter(Admin.email==email)
        .first()
    )
    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=403,
            detail="Admin account is inactive"
        )
    if not bcrypt.checkpw(
        data.password.encode("utf-8"),
        admin.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": admin.admin_id,
            "email": admin.email,
            "type": "admin",
            "exp": now + timedelta(hours=1)
        },
        SECRET_KEY,
        algorithm="HS256"
    )
        
    return {
        "message": "Admin login successful",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout():
    return {"message": "Logout successful"}