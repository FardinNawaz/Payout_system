
import os
import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException,Depends
from database import get_db
from sqlalchemy.orm import Session
from models import User
from routes.auth.models import (
    LoginRequest,
    LoginResponse,
)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing")

router = APIRouter(tags=["Auth"])


@router.post("/login")
def login(user: LoginRequest, db:Session=Depends(get_db)):
   
    email=str(user.email).lower()
    stored_user=(
        db.query(User)
        .filter(User.email==email)
        .first()
    )
    if not stored_user or not bcrypt.checkpw(
        user.password.encode(),stored_user.password_hash.encode()):

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )
    
    token = jwt.encode(
        {
            "email": stored_user.email,
            "role": stored_user.role
        },
        SECRET_KEY,
        algorithm="HS256"
        )
        
    return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer"
            }


@router.post("/logout")
def logout():
    return {"message": "Logout successful"}
