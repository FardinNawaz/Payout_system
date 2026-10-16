from pydantic import BaseModel, model_validator,Field , field_validator
from typing import Literal

class BankDetails(BaseModel):
    bank_name:str=Field(min_length=1,max_length=100)
    account_number:str=Field(min_length=4,max_length=100)
    ifsc_code:str=Field(min_length=4,max_length=50)

    @field_validator("bank_name")
    @classmethod
    def validate_bank_name(cls, value:str) -> str:
        value=value.strip()
        if not value:
            raise ValueError("Bank name cannot be empty")
        return value

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, value:str) -> str:
        value=value.strip()
        if not value:
            raise ValueError("Bank name cannot be empty")
        return value

    @field_validator("ifsc_code")
    @classmethod
    def validate_ifsc_code(cls, value:str) -> str:
        value=value.strip()
        if not value:
            raise ValueError("Bank name cannot be empty")
        return value


class UpiDetails(BaseModel):
    upi_id:str=Field(min_length=5,max_length=25)

    @field_validator("upi_id")
    @classmethod
    def validate_upi(cls,value:str) ->str:
        value=value.strip()
        if not value:
            raise ValueError("Upi id cannot be empty")
        return value
class BeneficiaryDetails(BaseModel):
    bank_accounts: list[BankDetails] =Field(default_factory=list)
    upi_accounts:list[UpiDetails]=Field(default_factory=list)

    @model_validator(mode="after")
    def validate_payment(self):
        if not self.bank_accounts or not self.upi_accounts:
            raise ValueError("Provide atleast one account details")
        return self
     

class BankAccountResponse(BaseModel):
    bank_id:str
    bank_name:str

class UpiAccountResponse(BaseModel):
    upi_account_id:str
    upi_id:str

class BeneficiaryData(BaseModel):
    beneficary_id:str
    bank_accounts:list[BankAccountResponse]
    upi_accounts:list[UpiAccountResponse]
class BeneficiaryResponse(BaseModel):
    message:str
    data:BeneficiaryData
    