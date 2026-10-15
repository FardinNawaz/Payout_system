
from pydantic import BaseModel, Field
from typing import Literal


class DocumentDetail(BaseModel):
    document_name: Literal["AADHAAR", "PAN", "VOTER_ID"]
    document_number: str = Field(min_length=1, max_length=50)
    document_pic_url: str = Field(min_length=1, max_length=500)


class DocumentData(BaseModel):
    document_id: str
    user_id: str
    document_name: str


class Document_Response(BaseModel):
    message: str
    data: DocumentData
