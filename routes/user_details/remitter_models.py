
import re

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


class BankDetails(BaseModel):
    bank_name: str = Field(min_length=1, max_length=100)
    account_number: str = Field(min_length=6, max_length=30)
    ifsc_code: str = Field(min_length=11, max_length=11)

    @field_validator("bank_name")
    @classmethod
    def validate_bank_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Bank name cannot be empty")
        return value

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("Account number must contain digits only")
        return value

    @field_validator("ifsc_code")
    @classmethod
    def validate_ifsc_code(cls, value: str) -> str:
        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", value):
            raise ValueError("Invalid IFSC code")

        return value


class UpiDetails(BaseModel):
    upi_id: str = Field(min_length=3, max_length=100)

    @field_validator("upi_id")
    @classmethod
    def validate_upi_id(cls, value: str) -> str:
        value = value.strip()

        if not re.fullmatch(r"[A-Za-z0-9._-]+@[A-Za-z0-9.-]+", value):
            raise ValueError("Invalid UPI ID format")

        return value


class PaymentDetailsRequest(BaseModel):
    bank_accounts: list[BankDetails] = Field(default_factory=list)
    upi_accounts: list[UpiDetails] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_payment_details(self):
        if not self.bank_accounts and not self.upi_accounts:
            raise ValueError(
                "Provide at least one bank account or UPI ID"
            )
        return self


class BankResponseData(BaseModel):
    bank_id: str


class UpiResponseData(BaseModel):
    upi_account_id: str


class PaymentDetailsData(BaseModel):
    bank_accounts: list[BankResponseData]
    upi_accounts: list[UpiResponseData]


class PaymentDetailsResponse(BaseModel):
    message: str
    data: PaymentDetailsData
