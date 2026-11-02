from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    model_validator
)


class BeneficiaryCreate(BaseModel):

    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str = Field(..., min_length=1, max_length=20)


class BeneficiaryResponse(BaseModel):

    beneficiary_id: str
    remitter_id: str
    name: str
    email: str | None
    phone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BeneficiaryAccountCreate(BaseModel):

    account_type: Literal["BANK", "UPI"]
    account_number: str | None = None
    ifsc_code: str | None = None
    upi_id: str | None = None

    @model_validator(mode="after")
    def validate_account_details(self):

        if self.account_type == "BANK":

            if not self.account_number:
                raise ValueError(
                    "Account number is required for BANK account"
                )

            if not self.ifsc_code:
                raise ValueError(
                    "IFSC code is required for BANK account"
                )

            if self.upi_id is not None:
                raise ValueError(
                    "UPI ID is not allowed for BANK account"
                )

        elif self.account_type == "UPI":

            if not self.upi_id:
                raise ValueError(
                    "UPI ID is required for UPI account"
                )

            if self.account_number is not None:
                raise ValueError(
                    "Account number is not allowed for UPI account"
                )

            if self.ifsc_code is not None:
                raise ValueError(
                    "IFSC code is not allowed for UPI account"
                )

        return self


class BeneficiaryAccountResponse(BaseModel):

    account_id: str
    beneficiary_id: str
    account_type: str
    account_number: str | None
    ifsc_code: str | None
    upi_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)