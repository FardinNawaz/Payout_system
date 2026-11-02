import bcrypt
import jwt

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db

from routes.organization.organization_model import (
    Organization,OrganizationUser
)

from routes.organization.users.organization_user_schema import (
    OrganizationUserCreate,OrganizationUserResponse
)

from routes.auth.auth import SECRET_KEY


router = APIRouter(
    prefix="/api/v1/organization/users",
    tags=["Organization Users"]
)

@router.post("/", response_model=OrganizationUserResponse, status_code=201)
def create_organization_user(
    data: OrganizationUserCreate,
    access_token: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )
    try:
        payload = jwt.decode(
            access_token.strip(),
            SECRET_KEY,
            algorithms=["HS256"]
        )
        if payload.get("token_type") != "organization":
            raise HTTPException(
                status_code=401,
                detail="Invalid organization token"
            )
        org_id = payload.get("org_id")

        if not org_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    organization = db.query(Organization).filter(
        Organization.org_id == org_id
    ).first()

    if not organization or not organization.is_active:
        raise HTTPException(
            status_code=403,
            detail="Organization not found or inactive"
        )

    email = str(data.email).lower()
    existing_user = db.query(OrganizationUser).filter(
        OrganizationUser.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User email already exists"
        )

    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = OrganizationUser(
        org_id=org_id,
        name=data.name,
        email=email,
        password_hash=password_hash,
        role="ORG_USER",
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User email already exists"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create organization user"
        )