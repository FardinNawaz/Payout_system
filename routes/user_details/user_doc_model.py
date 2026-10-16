
from pydantic import BaseModel, Field,field_validator
from typing import Literal


class DocumentDetail(BaseModel):
    document_name: Literal["AADHAAR", "PAN", "VOTER_ID"]
    document_number: str = Field(min_length=1, max_length=50)
    document_pic_url: str = Field(min_length=1, max_length=500)

    @field_validator("document_number")
    @classmethod
    def validate_document_number(cls,value:str) -> str:
        value=value.strip()
        if not value:
            raise ValueError("Document number can not be empty ")

        return value

    @field_validator("document_pic_url")
    @classmethod
    def validate_document_pic(cls,value:str) ->str:
        value=value.strip()
        if not value:
            raise ValueError("Document pic url not empty")
        return value

class DocumentRequest(BaseModel):
    documents:list[DocumentDetail] =Field(min_length=1)

class DocumentData(BaseModel):
    document_id: str
    user_id: str
    document_name: str


class Document_Response(BaseModel):
    message: str
    data: DocumentData
