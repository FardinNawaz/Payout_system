from pydantic import BaseModel, EmailStr, Field

class OrganizationLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class OrganizationLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"