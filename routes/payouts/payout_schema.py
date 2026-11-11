from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict
class PayoutRequest(BaseModel):

    remitter_id: str
    beneficiary_id: str
    account_id: str
    amount: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=2
    )

    currency: Literal["INR"] = "INR"
    payment_mode: Literal["BANK", "UPI"]

class PayoutResponse(BaseModel):

    id: str=Field(validation_alias="payout_id")
    org_id: str
    remitter_id: str
    beneficiary_id: str
    account_id: str
    amount: Decimal
    currency: str
    payment_mode: str
    status: str
    model_config = ConfigDict(from_attributes=True,populate_by_name=True)

