from pydantic import BaseModel, model_validator
from typing import Literal

class BeneficiaryDetails(BaseModel):
    type:Literal["Bank","Upi"]
    bank_name:str | None = None
    bank_number:str | None=None
    ifsc_code:str | None = None
    upi_id : str | None = None
    
    @model_validator(mode="after")