import bcrypt
import jwt
from fastapi import APIRouter, Header, HTTPException,Depends
from models import User
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from routes.auth.auth import  SECRET_KEY
from routes.admin.model import CreateUser, CreateUserResponse

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)


def check_admin(access_token: str, db: Session):
    try:
        payload = jwt.decode(
            access_token.strip(),
            SECRET_KEY,
            algorithms=["HS256"]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    email = payload.get("email")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    admin = db.scalars(
        select(User).where(User.email == email.lower())
    ).first()

    if admin is None:
        raise HTTPException(
            status_code=403,
            detail="Admin user not found"
        )

    if admin.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin can add users"
        )

    return admin

@router.post("/users")
def create_user(
    data: CreateUser,
    access_token: str = Header(),
    db:Session=Depends(get_db)
):

    try:
        admin = check_admin(access_token, db)
        email = str(data.email).lower()

        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )

        new_user = User(
            name=data.name,
            email=email,
            password_hash=bcrypt.hashpw(
                    data.password.encode(),
                    bcrypt.gensalt()
                ).decode(),
                role=data.role
        )
        try:
            db.add(new_user)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Email already exists or a database constraint was violated"
    )

        return {
                "message": "User created successfully",
                "created_by": admin.email,
                "user": {
                    "user_id": new_user.user_id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "role": new_user.role
            }
        }
    except Exception:
        db.rollback()
        raise

