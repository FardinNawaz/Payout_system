from pydantic import BaseModel,ConfigDict,Field,EmailStr,HttpUrl
from decimal import Decimal

class OrganizationCreate(BaseModel):
    org_name:str=Field(min_length=2,max_length=150)
    email:EmailStr
    phone: str = Field(min_length=10, max_length=12)
    password:str=Field(min_length=8)

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    org_id: str
    org_name: str
    email: EmailStr
    created_by_admin_id: str
    is_active: bool

class OrganizationWalletCreate(BaseModel):
    currency: str = Field(default="INR", min_length=3, max_length=3)

class OrganizationWalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wallet_id: str
    org_id: str
    balance: Decimal
    currency: str
    is_active: bool


class OrganizationAPICredentialResponse(BaseModel):
    org_id: str
    api_key: str
    api_secret: str


class OrganizationWebhookConfig(BaseModel):
    webhook_url: HttpUrl

class OrganizationWebhookResponse(BaseModel):
    org_id: str
    webhook_url: HttpUrl | None
    webhook_secret: str


class OrganizationWalletCredit(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=3, max_length=255)


class OrganizationWalletCreditResponse(BaseModel):
    org_id: str
    previous_balance: Decimal
    credited_amount: Decimal
    current_balance: Decimal
    description: str