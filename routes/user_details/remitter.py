
import jwt

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User, BankAccount, UPIAccount
from routes.auth.auth import SECRET_KEY

from routes.user_details.remitter_models import (
    PaymentDetailsRequest,
    PaymentDetailsResponse,
    PaymentDetailsData,
    BankResponseData,
    UpiResponseData,
)


router = APIRouter(
    prefix="/api/v1/user",
    tags=["Payment Details"],
)


@router.post(
    "/payment-details",
    response_model=PaymentDetailsResponse,
    status_code=201,
)
def add_payment_details(
    data: PaymentDetailsRequest,
    access_token: str = Header(),
    db: Session = Depends(get_db),
):
    # 1. Verify JWT
    try:
        payload = jwt.decode(
            access_token.strip(),
            SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    email = payload.get("email")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )


    user = (
        db.query(User)
        .filter(User.email == email.lower())
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    # 4. Check user role
    if user.role != "USER":
        raise HTTPException(
            status_code=403,
            detail="Only USER role can add payment details",
        )

    bank_records = []
    upi_records = []

    try:
        # 5. Add multiple bank accounts
        for item in data.bank_accounts:
            bank = BankAccount(
                user_id=user.user_id,
                bank_name=item.bank_name,
                account_number=item.account_number,
                ifsc=item.ifsc_code,
            )

            db.add(bank)
            bank_records.append(bank)

        # 6. Add multiple UPI accounts
        for item in data.upi_accounts:
            upi = UPIAccount(
                user_id=user.user_id,
                upi_id=item.upi_id,
            )

            db.add(upi)
            upi_records.append(upi)

        # 7. Save all records in one transaction
        db.commit()

        # Refresh saved records
        for bank in bank_records:
            db.refresh(bank)

        for upi in upi_records:
            db.refresh(upi)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "One or more bank accounts or UPI IDs "
                "already exist or violate a database constraint"
            ),
        )

    # 8. Return response in nested data format
    return PaymentDetailsResponse(
        message="Payment details added successfully",
        data=PaymentDetailsData(
            bank_accounts=[
                BankResponseData(
                    bank_id=str(bank.bank_id)
                )
                for bank in bank_records
            ],
            upi_accounts=[
                UpiResponseData(
                    upi_account_id=str(upi.upi_account_id)
                )
                for upi in upi_records
            ],
        ),
    )
