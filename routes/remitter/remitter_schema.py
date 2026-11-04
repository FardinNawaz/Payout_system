
from pydantic import BaseModel, ConfigDict, EmailStr,Field


class RemitterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str=Field(validation_alias="remitter_id")
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
