from pydantic import BaseModel,ConfigDict,Field,EmailStr,HttpUrl
from decimal import Decimal

class OrganizationCreate(BaseModel):
    org_name:str=Field(min_length=2,max_length=150)
    email:EmailStr
    phone: str = Field(min_length=10,max_length=10)
    password:str=Field(min_length=8)

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(validation_alias="org_id")
    org_name: str
    email: EmailStr
    created_by_admin_id: str
    is_active: bool

    model_config = ConfigDict(populate_by_name=True)
    
class OrganizationWalletCreate(BaseModel):
    currency: str = Field(default="INR", min_length=3, max_length=3)

class OrganizationWalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str= Field(validation_alias="org_id")
    org_id: str
    balance: Decimal
    currency: str
    is_active: bool

    model_config = ConfigDict(populate_by_name=True)


class OrganizationAPICredentialResponse(BaseModel):
    id: str= Field(validation_alias="org_id")
    api_key: str
    api_secret: str

    model_config = ConfigDict(populate_by_name=True)


class OrganizationWebhookConfig(BaseModel):
    webhook_url: HttpUrl

class OrganizationWebhookResponse(BaseModel):
    id: str= Field(validation_alias="org_id")
    webhook_url: HttpUrl | None
    webhook_secret: str

    model_config = ConfigDict(populate_by_name=True)


class OrganizationWalletCredit(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=3, max_length=255)


class OrganizationWalletCreditResponse(BaseModel):
    id: str= Field(validation_alias="org_id")
    previous_balance: Decimal
    credited_amount: Decimal
    current_balance: Decimal
    description: str


    model_config = ConfigDict(populate_by_name=True)