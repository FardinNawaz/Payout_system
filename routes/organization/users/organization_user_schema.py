from pydantic import BaseModel, EmailStr, Field, ConfigDict


class OrganizationUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)


class OrganizationUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    org_id: str
    name: str
    email: EmailStr
    role: str
    is_active: bool