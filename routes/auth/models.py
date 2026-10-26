from pydantic import BaseModel ,EmailStr,Field

class LoginRequest(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8)

class LoginResponse(BaseModel):
    message:str
    access_token:str
    token_type:str

class LogoutRequest(BaseModel):
    msg:str