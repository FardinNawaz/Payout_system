from pydantic import BaseModel ,ConfigDict, Field,EmailStr
from datetime import datetime

class AdminCreate(BaseModel):
    name:str =Field(min_length=2,max_length=100)
    email:EmailStr
    phone: str | None = Field(default=None, max_length=20)
    password:str=Field(min_length=8)

class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    admin_id: str
    name: str
    email: EmailStr
    phone: str | None
    is_super_admin: bool
    is_active: bool
    created_at: datetime
