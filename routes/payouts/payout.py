import uuid
import json
import hashlib
from fastapi import APIRouter, Depends,HTTPException,Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import(
    PAYOUT,
    APICLIENT,
    BankAccount,UPIAccount,IDEMPOTENCYKEY,
    BENEFICIARY,BENEFICIARYBANKAccount,BENEFICIARYUPIAccount
)
from services.api_auth import verify_api_request
from routes.payouts.payouts_models import PayoutRequest,PayoutResponse

router=APIRouter(
    prefix="/api/v1/payouts",
    tags=["Payouts"]
)
@router.post("",response_model=PayoutResponse,status_code=201)
async def create_payout(
    data:PayoutRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
    api_client:APICLIENT=Depends(verify_api_request),
    db:Session=Depends(get_db)
):
    user_id=api_client.user_id
    request_json = json.dumps(
    data.model_dump(mode="json"),
    sort_keys=True,
    separators=(",", ":"),
    )
    request_hash = hashlib.sha256(
        request_json.encode("utf-8")
    ).hexdigest()

    existing_key = (
        db.query(IDEMPOTENCYKEY)
        .filter(
            IDEMPOTENCYKEY.user_id == user_id,
            IDEMPOTENCYKEY.idempotency_key == idempotency_key,
        )
        .first()
    )

    if existing_key:
        if existing_key.request_hash != request_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency-Key already used with different request details",
            )

        if not existing_key.payout_id:
            raise HTTPException(
                status_code=409,
                detail="Request is still being processed",
            )

        original_payout = (
            db.query(PAYOUT)
            .filter(
                PAYOUT.payout_id == existing_key.payout_id,
                PAYOUT.user_id == user_id,
            )
            .first()
        )

        if original_payout is None:
            raise HTTPException(
                status_code=500,
                detail="Original payout could not be found",
            )

        return original_payout
    if data.payment_mode=="BANK":
        if not data.sender_bank_id or  data.sender_upi_account_id:
            raise HTTPException(
                status_code=400,
                detail="Provide only sender_bank_id for BANK payments"
            )
        sender_account=(db.query(BankAccount)
            .filter(
                BankAccount.bank_id==data.sender_bank_id,
                BankAccount.user_id==user_id
            ).first()
        )
        if sender_account is None:
            raise HTTPException(
                status_code=404,
                detail="Sender bank account not found"
            )

        if not data.beneficiary_bank_id or  data.beneficiary_upi_account_id:
            raise HTTPException(
                status_code=400,
                detail="Provide only beneficiary_bank_id for BANK payments"
            )
        destination=(
            db.query(BENEFICIARYBANKAccount)
            .join(
                BENEFICIARY,
                BENEFICIARY.beneficiary_id==BENEFICIARYBANKAccount.beneficiary_id
            )
            .filter(
                BENEFICIARYBANKAccount.bank_id == data.beneficiary_bank_id,
                BENEFICIARYBANKAccount.beneficiary_id == data.beneficiary_id,
                BENEFICIARY.user_id == user_id
            )
            .first()
        )

    else:
        if not data.sender_upi_account_id or data.sender_bank_id:
            raise HTTPException(
                status_code=400,
                detail="Provide only sender_upi_account_id for UPI payments"
            )
        sender_account=(
            db.query(UPIAccount)
            .filter(
                UPIAccount.upi_account_id==data.sender_upi_account_id,
                UPIAccount.user_id==user_id
            ).first()
        )
        if sender_account is None:
            raise HTTPException(
                status_code=404,
                detail="Sender Upi Account not found"
            )
        if not data.beneficiary_upi_account_id or data.beneficiary_bank_id:
            raise HTTPException(
                status_code=400,
                detail="Provide only beneficiary_upi_account_id for UPI payments"
            )

        destination=(
            db.query(BENEFICIARYUPIAccount)
            .join(
                BENEFICIARY,
                BENEFICIARY.beneficiary_id==BENEFICIARYUPIAccount.beneficiary_id
            )
            .filter(
                BENEFICIARYUPIAccount.upi_account_id==data.beneficiary_upi_account_id,
                BENEFICIARY.beneficiary_id==data.beneficiary_id,
                BENEFICIARY.user_id==user_id
            )
            .first()
        )
    if destination is None:
        raise HTTPException(
            status_code=404,
            detail="Beneficiary or destination account not found",
        )

    # existing=(db.query(PAYOUT)
    #     .filter(PAYOUT.reference_id==data.reference_id).first())


    # if existing:
    #     raise HTTPException(
    #         status_code=409,
    #         detail="Reference ID already used",
    #     )

    reference_id = f"REF-{uuid.uuid4().hex}"
    payout = PAYOUT(
        user_id=user_id,
        beneficiary_id=data.beneficiary_id,
        sender_bank_id=data.sender_bank_id,
        sender_upi_account_id=data.sender_upi_account_id,
        beneficiary_bank_id=data.beneficiary_bank_id,
        beneficiary_upi_account_id=data.beneficiary_upi_account_id,
        reference_id=reference_id,
        amount=data.amount,
        currency=data.currency,
        payment_mode=data.payment_mode,
        status="PENDING",
    )

    key_record = IDEMPOTENCYKEY(
        user_id=user_id,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )

    try:
        db.add(payout)
        db.flush()

        key_record.payout_id = payout.payout_id
        db.add(key_record)

        db.commit()
        db.refresh(payout)
    except IntegrityError:
        db.rollback()
        concurrent_key = (
            db.query(IDEMPOTENCYKEY)
            .filter(
                IDEMPOTENCYKEY.user_id == user_id,
                IDEMPOTENCYKEY.idempotency_key == idempotency_key,
            )
            .first()
        )

        if concurrent_key:
            if concurrent_key.request_hash != request_hash:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency-Key already used with different request details",
                )

            if concurrent_key.payout_id:
                original_payout = (
                    db.query(PAYOUT)
                    .filter(
                        PAYOUT.payout_id == concurrent_key.payout_id,
                        PAYOUT.user_id == user_id,
                    )
                    .first()
                )
                if original_payout:
                    return original_payout

        raise HTTPException(
            status_code=409,
            detail="Database conflict; retry with the same Idempotency-Key",
        )

    return payout
