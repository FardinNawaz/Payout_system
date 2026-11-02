from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db

from routes.organization.organization_model import Organization
from routes.organization.auth.organization_auth_schema import (
    OrganizationLoginRequest,
    OrganizationLoginResponse
)
from routes.auth.auth import SECRET_KEY

router = APIRouter(
    prefix="/api/v1/organization/auth",
    tags=["Organization Authentication"]
)

@router.post("/login", response_model=OrganizationLoginResponse)
def organization_login(
    data: OrganizationLoginRequest,
    db: Session = Depends(get_db)
):
    email = str(data.email).lower()

    organization = db.query(Organization).filter(
        Organization.email == email
    ).first()

    if not organization:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=403,
            detail="Organization is inactive"
        )

    password_valid = bcrypt.checkpw(
        data.password.encode("utf-8"),
        organization.password_hash.encode("utf-8")
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    now = datetime.now(timezone.utc)

    access_token = jwt.encode(
        {
            "sub": organization.org_id,
            "org_id": organization.org_id,
            "token_type": "organization",
            "exp": now + timedelta(hours=1)
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return OrganizationLoginResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/logout")
def logout():
    return {"message": "Logout successful"}