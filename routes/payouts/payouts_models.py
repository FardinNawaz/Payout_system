from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class PayoutRequest(BaseModel):

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    currency: Literal["INR"] = "INR"
    payment_mode: Literal["BANK", "UPI"]

    sender_bank_id: str | None = None
    sender_upi_account_id: str | None = None

    beneficiary_id: str
    beneficiary_bank_id: str | None = None
    beneficiary_upi_account_id: str | None = None

class PayoutResponse(BaseModel):
    payout_id: str
    reference_id: str
    beneficiary_id: str
    amount: Decimal
    currency: str
    payment_mode: str
    status: str

    model_config = ConfigDict(from_attributes=True)
