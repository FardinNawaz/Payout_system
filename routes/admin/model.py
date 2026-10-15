from pydantic import BaseModel , Field,EmailStr
from typing import Literal

class CreateUser(BaseModel):
    name:str
    email:EmailStr
    password:str=Field(min_length=8)
    role:Literal["ADMIN","USER"]

class CreatedUserResponse(BaseModel):
    user_id:str
    name: str
    email:EmailStr
    role:str
class CreateUserResponse(BaseModel):
    message:str
    created_by:EmailStr
    user:CreatedUserResponse
