from pydantic import BaseModel,EmailStr
class Usercheck(BaseModel):
    email:EmailStr
