
from pydantic import BaseModel, ConfigDict, EmailStr


class RemitterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    remitter_id: str
    org_id: str
    name: str
    email: EmailStr
    phone: str
    is_active: bool


class RemitterDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    remitter_id: str
    document_type: str
    document_number: str | None
