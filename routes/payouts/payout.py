import os
import time
import uuid
import hmac
import hashlib

from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)
from routes.payouts.escrowstack import send_bank_payout
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from cryptography.fernet import Fernet, InvalidToken
from database import get_db

from routes.organization.organization_model import(
    Organization,
    OrganizationAPICredential,
    OrganizationWallet
)

from routes.remitter.remitter_models import Remitter

from routes.organization.beneficiary.beneficiary_models import(
    Beneficiary,BeneficiaryAccount
)
from routes.payouts.payouts_models import Payout
from routes.payouts.payout_schema import PayoutRequest,PayoutResponse

router=APIRouter(
    prefix="/api/v1/payouts",
    tags=["Payouts"]
)
TIMESTAMP_TOLERANCE=300

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

    current_time=int(time.time())
    if abs(current_time - request_timestamp) > TIMESTAMP_TOLERANCE:
        raise HTTPException(
            status_code=401,
            detail="Request timestamp expired"
        )
    credentials = (
        db.query(OrganizationAPICredential)
        .filter(
            OrganizationAPICredential.api_key == api_key
        )
        .first()
    )
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    organization = (
        db.query(Organization)
        .filter(
            Organization.org_id == credentials.org_id
        )
        .first()
    )

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

    except (InvalidToken):
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt API secret"
        )
        

    expected_signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()


    if not hmac.compare_digest(
        expected_signature,
        signature
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    return organization

@router.post(
    "",
    response_model=PayoutResponse,
    status_code=201
)
def create_payout(
    data:PayoutRequest,

    api_key:str=Header(...,alias="X-API-KEY"),
    timestamp: str = Header(..., alias="X-TIMESTAMP"),
    signature: str = Header(..., alias="X-SIGNATURE"),
    
    db: Session = Depends(get_db)
):
    amount = data.amount
    path = "/api/v1/payouts"
    message_parts = [
        timestamp,
        "POST",
        path,
        api_key,
        data.remitter_id,
        data.beneficiary_id,
        data.account_id,
        format(amount, ".2f"),
        data.currency,
        data.payment_mode
    ]
    message = "\n".join(message_parts)

    organization = authenticate_organization(
        api_key=api_key,
        timestamp=timestamp,
        signature=signature,
        message=message,
        db=db
    )

    try:
        remitter = (
            db.query(Remitter)
            .filter(
                Remitter.remitter_id == data.remitter_id,
                Remitter.org_id == organization.org_id,
                Remitter.is_active.is_(True)
            )
            .first()
        )
        if not remitter:
            raise HTTPException(
                status_code=404,
                detail="Remitter not found or inactive"
            )

        beneficiary = (
            db.query(Beneficiary)
            .filter(
                Beneficiary.beneficiary_id == data.beneficiary_id,
                Beneficiary.remitter_id == remitter.remitter_id
            )
            .first()
        )

        if not beneficiary:
            raise HTTPException(
                status_code=404,
                detail="Beneficiary not found for this remitter"
            )

        destination = (
            db.query(BeneficiaryAccount)
            .filter(
                BeneficiaryAccount.account_id == data.account_id,
                BeneficiaryAccount.beneficiary_id == beneficiary.beneficiary_id
            )
            .first()
        )

        if not destination:
            raise HTTPException(
                status_code=404,
                detail="Beneficiary account not found"
            )

        if destination.account_type != data.payment_mode:
            raise HTTPException(
                status_code=400,
                detail="Payment mode does not match beneficiary account type"
            )

        wallet = (
            db.query(OrganizationWallet)
            .filter(
                OrganizationWallet.org_id == organization.org_id
            )
            .first()
        )

        if not wallet:
            raise HTTPException(
                status_code=404,
                detail="Organization wallet not found"
            )


        if not wallet.is_active:
            raise HTTPException(
                status_code=403,
                detail="Organization wallet is inactive"
            )

        if wallet.currency != data.currency:
            raise HTTPException(
                status_code=400,
                detail="Wallet currency does not match payout currency"
            )

        if wallet.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient wallet balance"
            )


        payout = Payout(
            org_id=organization.org_id,
            wallet_id=wallet.wallet_id,
            remitter_id=remitter.remitter_id,
            beneficiary_id=beneficiary.beneficiary_id,
            account_id=destination.account_id,
            amount=amount,
            currency=data.currency,
            payment_mode=data.payment_mode,
            status="PENDING"
        )

        db.add(payout)
        db.commit()
        db.refresh(payout)

        if data.payment_mode == "BANK":
            gateway_response = send_bank_payout(
                payout,
                beneficiary,
                destination
            )

            print("EscrowStack response:", gateway_response)

        return payout



      
    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as e:
        db.rollback()

        print("PAYOUT INTEGRITY ERROR:", repr(e))

        raise HTTPException(
            status_code=409,
            detail="Payout database conflict"
        )

    except Exception as e:
        db.rollback()

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Failed to create payout"
        )
