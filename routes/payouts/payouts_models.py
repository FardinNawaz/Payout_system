from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class PayoutRequest(BaseModel):
    reference_id: str = Field(min_length=1, max_length=100)
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

    @field_validator("reference_id")
    @classmethod
    def validate_reference_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Reference ID cannot be empty")
        return value


class PayoutResponse(BaseModel):
    payout_id: str
    reference_id: str
    beneficiary_id: str
    amount: Decimal
    currency: str
    payment_mode: str
    status: str

    model_config = ConfigDict(from_attributes=True)
