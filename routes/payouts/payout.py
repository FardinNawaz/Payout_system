from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import(
    PAYOUT,
    APICLIENT,
    BankAccount,UPIAccount,
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
    api_client:APICLIENT=Depends(verify_api_request),
    db:Session=Depends(get_db)
):
    user_id=api_client.user_id
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
            .filter(BENEFICIARYBANKAccount.beneficiary_id==data.beneficiary_bank_id,
                BENEFICIARY.beneficiary_id==data.beneficiary_id,
                BENEFICIARY.user_id==user_id).first()
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

    existing=(db.query(PAYOUT)
        .filter(PAYOUT.reference_id==data.reference_id).first())

    if existing:
        if existing.user_id!=user_id:
            raise HTTPException(
                status_code=409,
                detail="Reference ID already used",
            )
        if(
            existing.beneficiary_id != data.beneficiary_id
            or existing.amount != data.amount
            or existing.payment_mode != data.payment_mode
        ):
            raise HTTPException(
                status_code=409,
                detail="Reference ID already used with different payout details",
            )
        return existing

    payout = PAYOUT(
        user_id=user_id,
        beneficiary_id=data.beneficiary_id,
        sender_bank_id=data.sender_bank_id,
        sender_upi_account_id=data.sender_upi_account_id,
        beneficiary_bank_id=data.beneficiary_bank_id,
        beneficiary_upi_account_id=data.beneficiary_upi_account_id,
        reference_id=data.reference_id,
        amount=data.amount,
        currency=data.currency,
        payment_mode=data.payment_mode,
        status="PENDING",
    )

    try:
        db.add(payout)
        db.commit()
        db.refresh(payout)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate payout reference",
        )

    return payout



@router.get("/{payout_id}", response_model=PayoutResponse)
async def get_payout(
    payout_id: str,
    api_client: APICLIENT = Depends(verify_api_request),
    db: Session = Depends(get_db),
):
    payout = (
        db.query(PAYOUT)
        .filter(
            PAYOUT.payout_id == payout_id,
            PAYOUT.user_id == api_client.user_id,
        )
        .first()
    )

    if payout is None:
        raise HTTPException(
            status_code=404,
            detail="Payout not found",
        )

    return payout