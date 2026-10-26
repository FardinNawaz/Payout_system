import jwt
from fastapi import APIRouter,Header,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import (
    User,
    BENEFICIARY,
    BENEFICIARYBANKAccount,BENEFICIARYUPIAccount
)

from routes.auth.auth import SECRET_KEY
from routes.user_details.beneficiary.beneficary_models import(
    BeneficiaryDetails,
    BeneficiaryResponse,
    BeneficiaryData,
    BankAccountResponse,
    UpiAccountResponse
)

router = APIRouter(
    prefix="/api/v1/user",
    tags=["Beneficiary"]
)

@router.post("/beneficiary")
def add_beneficiary(
    data:BeneficiaryDetails,
    access_token:str=Header(),
    db:Session=Depends(get_db)
):
    try:
        payload=jwt.decode(
            access_token.strip(),
            SECRET_KEY,
            algorithms=["HS256"]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    email=payload.get("email")
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token Payload"
        )
    user=(
        db.query(User).
        filter(User.email==email.lower()).first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="user not found"
        )
    if user.role !="USER":
        raise HTTPException(
            status_code=403,
            detail="Only user can add"
        )
    for item in data.bank_accounts:
        existing_account = (
            db.query(BENEFICIARYBANKAccount)
            .join(
                BENEFICIARY,
                BENEFICIARY.beneficiary_id
                == BENEFICIARYBANKAccount.beneficiary_id
            )
            .filter(
                BENEFICIARY.user_id == user.user_id,
                BENEFICIARYBANKAccount.account_number
                == item.account_number
            )
            .first()
        )

        if existing_account:
            raise HTTPException(
                status_code=409,
                detail="Bank account already registered"
            )
    for item in data.upi_accounts:
        existing_upi = (
            db.query(BENEFICIARYUPIAccount)
            .join(
                BENEFICIARY,
                BENEFICIARY.beneficiary_id
                == BENEFICIARYUPIAccount.beneficiary_id
            )
            .filter(
                BENEFICIARY.user_id == user.user_id,
                BENEFICIARYUPIAccount.upi_id == item.upi_id
            )
            .first()
        )

        if existing_upi:
            raise HTTPException(
                status_code=409,
                detail="UPI ID already registered"
            )

    try:
        beneficiary=BENEFICIARY(
            user_id=user.user_id,
            beneficiary_name=data.beneficiary_name
        )
        db.add(beneficiary)

        db.flush()

        bank_records=[]
        for item in data.bank_accounts:
            bank=BENEFICIARYBANKAccount(
                beneficiary_id=beneficiary.beneficiary_id,
                bank_name=item.bank_name,
                account_number=item.account_number,
                ifsc_code=item.ifsc_code   
            )
            db.add(bank)
            bank_records.append(bank)

        upi_records=[]

        for item in data.upi_accounts:
            upi=BENEFICIARYUPIAccount(
                beneficiary_id=beneficiary.beneficiary_id,
                upi_id=item.upi_id
            )

            db.add(upi)
            upi_records.append(upi)

        db.commit()

        db.refresh(beneficiary)
        for bank in bank_records:
            db.refresh(bank)
        for upi in upi_records:
            db.refresh(upi)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate bank account or upi"
        )
    return BeneficiaryResponse(
        message="Beneficiary added successfully",
        data=BeneficiaryData(
            beneficiary_id=beneficiary.beneficiary_id,
            beneficiary_name=beneficiary.beneficiary_name,
            bank_accounts=[
                BankAccountResponse(
                    bank_id=bank.bank_id,
                    bank_name=bank.bank_name,
                )
                for bank in bank_records
            ],
            upi_accounts=[
                UpiAccountResponse(
                    upi_account_id=upi.upi_account_id,
                    upi_id=upi.upi_id,
                )
                for upi in upi_records
            ],
        ),
    )        