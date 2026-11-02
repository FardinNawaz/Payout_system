
import os
import time
import hmac
import hashlib

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

from database import get_db

from routes.organization.organization_model import (
    Organization,
    OrganizationAPICredential
)

from routes.remitter.remitter_models import Remitter

from routes.organization.beneficiary.beneficiary_models import (
    Beneficiary,
    BeneficiaryAccount
)

from routes.organization.beneficiary.beneficiary_schema import (
    BeneficiaryCreate,
    BeneficiaryResponse,
    BeneficiaryAccountCreate,
    BeneficiaryAccountResponse
)

load_dotenv()

router = APIRouter(
    prefix="/api/v1/remitters/{remitter_id}/beneficiaries",
    tags=["Beneficiary"]
)

TIMESTAMP_TOLERANCE = 300

def authenticate_organization(
    api_key: str,
    timestamp: str,
    signature: str,
    message: str,
    db: Session
):

    try:
        request_timestamp = int(timestamp)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid timestamp"
        )

    current_time = int(time.time())

    if abs(current_time - request_timestamp) > TIMESTAMP_TOLERANCE:
        raise HTTPException(
            status_code=401,
            detail="Request timestamp expired"
        )

    credentials = db.query(
        OrganizationAPICredential
    ).filter(
        OrganizationAPICredential.api_key == api_key
    ).first()

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    organization = db.query(Organization).filter(
        Organization.org_id == credentials.org_id
    ).first()

    if not organization or not organization.is_active:
        raise HTTPException(
            status_code=403,
            detail="Organization inactive or not found"
        )

    encryption_key = os.getenv("API_SECRET_ENCRYPTION_KEY")

    if not encryption_key:
        raise HTTPException(
            status_code=500,
            detail="Encryption key not configured"
        )

    try:
        cipher = Fernet(encryption_key.encode())

        api_secret = cipher.decrypt(
            credentials.api_secret.encode()
        ).decode()

    except (InvalidToken, ValueError):
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt API secret"
        )

    print("\n========== BACKEND DEBUG ==========")
    print("MESSAGE:", repr(message))
    print("API KEY:", api_key)
    print("TIMESTAMP:", timestamp)
    print("==================================\n")

    expected_signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    print("EXPECTED SIGNATURE:", expected_signature)
    print("RECEIVED SIGNATURE:", signature)

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    return organization

def verify_remitter(
    remitter_id: str,
    organization: Organization,
    db: Session
):

    remitter = db.query(Remitter).filter(
        Remitter.remitter_id == remitter_id,
        Remitter.org_id == organization.org_id,
        Remitter.is_active.is_(True)
    ).first()

    if not remitter:
        raise HTTPException(
            status_code=404,
            detail="Remitter not found or does not belong to this organization"
        )

    return remitter

@router.post(
    "/",
    response_model=BeneficiaryResponse,
    status_code=201
)
def create_beneficiary(

    remitter_id: str,

    data: BeneficiaryCreate,

    api_key: str = Header(..., alias="X-API-KEY"),
    timestamp: str = Header(..., alias="X-TIMESTAMP"),
    signature: str = Header(..., alias="X-SIGNATURE"),

    db: Session = Depends(get_db)

):

    name = data.name.strip()
    email = str(data.email).strip().lower() if data.email else ""
    phone = data.phone.strip()

    message = "\n".join([
        timestamp,
        "POST",
        f"/api/v1/remitters/{remitter_id}/beneficiaries/",
        api_key,
        remitter_id,
        name,
        email,
        phone
    ])

    organization = authenticate_organization(
        api_key=api_key,
        timestamp=timestamp,
        signature=signature,
        message=message,
        db=db
    )

    remitter = verify_remitter(
        remitter_id=remitter_id,
        organization=organization,
        db=db
    )

    new_beneficiary = Beneficiary(
        remitter_id=remitter.remitter_id,
        name=name,
        email=email or None,
        phone=phone
    )

    try:
        db.add(new_beneficiary)
        db.commit()
        db.refresh(new_beneficiary)

        return new_beneficiary

    except IntegrityError as e:
        db.rollback()
        print("INTEGRITY ERROR:", repr(e))
        raise HTTPException(
            status_code=409,
            detail="Database constraint error"
        )

    except Exception as e:
        db.rollback()
        print("BENEFICIARY ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to create beneficiary"
        )

@router.post(
    "/{beneficiary_id}/accounts",
    response_model=BeneficiaryAccountResponse,
    status_code=201
)
def add_beneficiary_account(

    remitter_id: str,
    beneficiary_id: str,

    data: BeneficiaryAccountCreate,

    api_key: str = Header(..., alias="X-API-KEY"),
    timestamp: str = Header(..., alias="X-TIMESTAMP"),
    signature: str = Header(..., alias="X-SIGNATURE"),

    db: Session = Depends(get_db)

):

    account_type = data.account_type

    account_number = (
        data.account_number.strip()
        if data.account_number is not None
        else ""
    )

    ifsc_code = (
        data.ifsc_code.strip().upper()
        if data.ifsc_code is not None
        else ""
    )

    upi_id = (
        data.upi_id.strip()
        if data.upi_id is not None
        else ""
    )

    path = (
        f"/api/v1/remitters/{remitter_id}/beneficiaries/"
        f"{beneficiary_id}/accounts"
    )

    message = "\n".join([
        timestamp,
        "POST",
        path,
        api_key,
        remitter_id,
        beneficiary_id,
        account_type,
        account_number,
        ifsc_code,
        upi_id
    ])

    organization = authenticate_organization(
        api_key=api_key,
        timestamp=timestamp,
        signature=signature,
        message=message,
        db=db
    )


    remitter = verify_remitter(
        remitter_id=remitter_id,
        organization=organization,
        db=db
    )


    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.beneficiary_id == beneficiary_id,
        Beneficiary.remitter_id == remitter.remitter_id
    ).first()

    if not beneficiary:
        raise HTTPException(
            status_code=404,
            detail="Beneficiary not found for this remitter"
        )

    new_account = BeneficiaryAccount(
        beneficiary_id=beneficiary.beneficiary_id,
        account_type=account_type,
        account_number=account_number or None,
        ifsc_code=ifsc_code or None,
        upi_id=upi_id or None
    )

    try:
        db.add(new_account)
        db.commit()
        db.refresh(new_account)

        return new_account

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Account already exists or violates a database constraint"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to add beneficiary account"
        )
