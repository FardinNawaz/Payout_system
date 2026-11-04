
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
    BeneficiaryWithAccountsResponse
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
    # print("Received API key:", repr(api_key))
    credentials = db.query(
        OrganizationAPICredential
    ).filter(
        OrganizationAPICredential.api_key == api_key
    ).first()

    # print("Credentials found:", credentials is not None)

    if credentials:
        print("Organization ID:", credentials.org_id)
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    organization = db.query(Organization).filter(
        Organization.org_id == credentials.org_id
    ).first()

    if not organization :
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


    expected_signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    

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
    response_model=BeneficiaryWithAccountsResponse,
    status_code=201
)

def create_or_add_beneficiary(

    remitter_id: str,

    data: BeneficiaryCreate,

    api_key: str = Header(..., alias="X-API-KEY"),
    timestamp: str = Header(..., alias="X-TIMESTAMP"),
    signature: str = Header(..., alias="X-SIGNATURE"),

    db: Session = Depends(get_db)

):
    name = data.name.strip() if data.name else ""
    email = str(data.email).strip().lower() if data.email else ""
    phone = data.phone.strip() if data.phone else ""

    path = f"/api/v1/remitters/{remitter_id}/beneficiaries/"

    message_parts = [
        timestamp,
        "POST",
        path,
        api_key,
        remitter_id,
        data.id or "",
        name,
        email,
        phone
    ]

    for account in data.accounts:

        message_parts.extend([
            account.account_type,
            account.account_number or "",
            account.ifsc_code or "",
            account.upi_id or ""
        ])

    message = "\n".join(message_parts)

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

    try:
        if data.id is None:

            existing_beneficiary = db.query(Beneficiary).filter(
                Beneficiary.remitter_id == remitter.remitter_id,
                Beneficiary.phone == phone
            ).first()

            if existing_beneficiary:
                raise HTTPException(
                    status_code=409,
                    detail="Beneficiary already exists for this remitter"
                )

            beneficiary = Beneficiary(
                remitter_id=remitter.remitter_id,
                name=name,
                email=email or None,
                phone=phone
            )

            db.add(beneficiary)
            db.flush()

        else:

            beneficiary = db.query(Beneficiary).filter(
                Beneficiary.beneficiary_id == data.id,
                Beneficiary.remitter_id == remitter.remitter_id
            ).first()

            if not beneficiary:
                raise HTTPException(
                    status_code=404,
                    detail="Beneficiary not found for this remitter"
                )
        new_accounts=[]
        for account in data.accounts:

            new_account = BeneficiaryAccount(
                beneficiary_id=beneficiary.beneficiary_id,
                account_type=account.account_type,
                account_number=account.account_number,
                ifsc_code=account.ifsc_code,
                upi_id=account.upi_id
            )

            db.add(new_account)
            new_accounts.append(new_account)

        db.commit()

        db.refresh(beneficiary)

        for account in new_accounts:
            db.refresh(account)

        return {
            "id": beneficiary.beneficiary_id,
            "remitter_id": beneficiary.remitter_id,
            "name": beneficiary.name,
            "email": beneficiary.email,
            "phone": beneficiary.phone,
            "created_at": beneficiary.created_at,
            "accounts": new_accounts
        }
    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as e:
        db.rollback()
        print("INTEGRITY ERROR:", repr(e))

        raise HTTPException(
            status_code=409,
            detail="Account already exists or violates a database constraint"
        )

    except Exception as e:
        db.rollback()

        import traceback
        print("BENEFICIARY ERROR:", repr(e))
        # traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Failed to process beneficiary and accounts"
        )











# def create_beneficiary(

#     remitter_id: str,

#     data: BeneficiaryCreate,

#     api_key: str = Header(..., alias="X-API-KEY"),
#     timestamp: str = Header(..., alias="X-TIMESTAMP"),
#     signature: str = Header(..., alias="X-SIGNATURE"),

#     db: Session = Depends(get_db)

# ):

#     name = data.name.strip()
#     email = str(data.email).strip().lower() if data.email else ""
#     phone = data.phone.strip()

#     message = "\n".join([
#         timestamp,
#         "POST",
#         f"/api/v1/remitters/{remitter_id}/beneficiaries/",
#         api_key,
#         remitter_id,
#         name,
#         email,
#         phone
#     ])

#     organization = authenticate_organization(
#         api_key=api_key,
#         timestamp=timestamp,
#         signature=signature,
#         message=message,
#         db=db
#     )
    

#     remitter = verify_remitter(
#         remitter_id=remitter_id,
#         organization=organization,
#         db=db
#     )

#     existing_beneficiary = db.query(Beneficiary).filter(
#         Beneficiary.remitter_id == remitter.remitter_id,
#         Beneficiary.phone == phone
#     ).first()

#     if existing_beneficiary:
#         raise HTTPException(
#             status_code=409,
#             detail="Beneficiary already exists for this remitter"
#         )

#     new_beneficiary = Beneficiary(
#         remitter_id=remitter.remitter_id,
#         name=name,
#         email=email or None,
#         phone=phone
#     )

#     try:
#         db.add(new_beneficiary)
#         db.commit()
#         db.refresh(new_beneficiary)

#         return new_beneficiary

#     except IntegrityError as e:
#         db.rollback()
#         print("INTEGRITY ERROR:", repr(e))
#         raise HTTPException(
#             status_code=409,
#             detail="Database constraint error"
#         )

#     except Exception as e:
#         db.rollback()
#         print("BENEFICIARY ERROR:", repr(e))
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to create beneficiary"
#         )

# @router.post(
#     "/{beneficiary_id}/accounts",
#     response_model=BeneficiaryAccountResponse,
#     status_code=201
# )
# def add_beneficiary_account(

#     remitter_id: str,
#     beneficiary_id: str,

#     data: BeneficiaryAccountCreate,

#     api_key: str = Header(..., alias="X-API-KEY"),
#     timestamp: str = Header(..., alias="X-TIMESTAMP"),
#     signature: str = Header(..., alias="X-SIGNATURE"),

#     db: Session = Depends(get_db)

# ):

#     account_type = data.account_type

#     account_number = (
#         data.account_number.strip()
#         if data.account_number is not None
#         else ""
#     )

#     ifsc_code = (
#         data.ifsc_code.strip().upper()
#         if data.ifsc_code is not None
#         else ""
#     )

#     upi_id = (
#         data.upi_id.strip()
#         if data.upi_id is not None
#         else ""
#     )

#     path = (
#         f"/api/v1/remitters/{remitter_id}/beneficiaries/"
#         f"{beneficiary_id}/accounts"
#     )

#     message = "\n".join([
#         timestamp,
#         "POST",
#         path,
#         api_key,
#         remitter_id,
#         beneficiary_id,
#         account_type,
#         account_number,
#         ifsc_code,
#         upi_id
#     ])

#     organization = authenticate_organization(
#         api_key=api_key,
#         timestamp=timestamp,
#         signature=signature,
#         message=message,
#         db=db
#     )


#     remitter = verify_remitter(
#         remitter_id=remitter_id,
#         organization=organization,
#         db=db
#     )


#     beneficiary = db.query(Beneficiary).filter(
#         Beneficiary.beneficiary_id == beneficiary_id,
#         Beneficiary.remitter_id == remitter.remitter_id
#     ).first()

#     if not beneficiary:
#         raise HTTPException(
#             status_code=404,
#             detail="Beneficiary not found for this remitter"
#         )

#     new_account = BeneficiaryAccount(
#         beneficiary_id=beneficiary.beneficiary_id,
#         account_type=account_type,
#         account_number=account_number or None,
#         ifsc_code=ifsc_code or None,
#         upi_id=upi_id or None
#     )

#     try:
#         db.add(new_account)
#         db.commit()
#         db.refresh(new_account)

#         return new_account

#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(
#             status_code=409,
#             detail="Account already exists or violates a database constraint"
#         )

#     except Exception:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to add beneficiary account"
#         )
