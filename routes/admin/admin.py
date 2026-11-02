
import bcrypt
import jwt
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db

from routes.auth.auth import  SECRET_KEY
from routes.admin.admin_model import Admin
from routes.admin.schema import AdminCreate, AdminResponse

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

    admin_id = payload.get("sub")

    if not admin_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    admin = db.query(Admin).filter(Admin.admin_id==admin_id).first()

    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=403,
            detail="Admin not found or inactive"
        )


    return admin

@router.post("/admins")
def create_user(
    data: AdminCreate,
    access_token: str| None = Header(default=None),
    db:Session=Depends(get_db)
):

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )

    current_admin=check_admin(access_token,db)
    email = str(data.email).lower()

    existing_admin = db.query(Admin).filter(Admin.email==email).first()

    if existing_admin:
        raise HTTPException(
            status_code=409,
            detail="Admin email already exists"
        )

    new_admin = Admin(
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=bcrypt.hashpw(
            data.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8"),
        is_active=True
    )

    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        return new_admin

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Admin email already exists"
        )
