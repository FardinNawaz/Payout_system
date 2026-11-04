from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    model_validator
)


class BeneficiaryAccountCreate(BaseModel):

    account_type: Literal["BANK", "UPI"]
    account_number: str | None = None
    ifsc_code: str | None = None
    upi_id: str | None = None

    @model_validator(mode="after")
    def validate_account_details(self):

        if self.account_number is not None:
            self.account_number = self.account_number.strip()

        if self.ifsc_code is not None:
            self.ifsc_code = self.ifsc_code.strip().upper()

        if self.upi_id is not None:
            self.upi_id = self.upi_id.strip()
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



class BeneficiaryCreate(BaseModel):

    id: str | None = None
    name: str|None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str|None= Field(default=None, min_length=10, max_length=10)

    accounts: list[BeneficiaryAccountCreate] = Field(..., min_length=1)


    @model_validator(mode="after")
    def validate_beneficiary_details(self):

        if self.id is None:

            if not self.name:
                raise ValueError("Name is required for new beneficiary")

            if not self.phone:
                raise ValueError("Phone is required for new beneficiary")
        else:

            if self.name is not None or self.email is not None or self.phone is not None:
                raise ValueError(
                    "Do not send beneficiary details when beneficiary_id is provided"
                )

        return self

class BeneficiaryResponse(BaseModel):

    id: str  = Field(validation_alias="beneficiary_id")
    remitter_id: str
    name: str
    email: str | None
    phone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class BeneficiaryAccountResponse(BaseModel):

    account_id: str
    id: str 
    account_type: str
    account_number: str | None
    ifsc_code: str | None
    upi_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BeneficiaryWithAccountsResponse(BaseModel):

    id: str = Field(validation_alias="beneficiary_id")
    remitter_id: str
    name: str
    email: str | None
    phone: str
    created_at: datetime
    accounts: list[BeneficiaryAccountResponse]