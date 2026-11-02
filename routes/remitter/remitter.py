
import time
import hmac
import hashlib
import os

from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session


from cryptography.fernet import Fernet, InvalidToken

from PIL import Image, UnidentifiedImageError

from database import get_db

from routes.organization.organization_model import (
    Organization,
    OrganizationAPICredential
)

from routes.remitter.remitter_models import (
    Remitter,
    RemitterDocument
)


router = APIRouter(
    prefix="/api/v1/remitters",
    tags=["Remitter"]
)

MAX_FILE_SIZE = 5 * 1024 * 1024
TIMESTAMP_TOLERANCE = 300


def authenticate_organization(
    api_key,
    timestamp,
    signature,
    name,
    email,
    phone,
    document_type,
    document_number,
    db
):

    try:
        request_timestamp = int(timestamp)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid timestamp"
        )

    current_time = int(time.time())

    if abs(current_time - request_timestamp) > TIMESTAMP_TOLERANCE:
        raise HTTPException(
            status_code=401,
            detail="Request timestamp expired"
        )

    credentials = db.query(
        OrganizationAPICredential
    ).filter(
        OrganizationAPICredential.api_key == api_key
    ).first()

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    organization = db.query(Organization).filter(
        Organization.org_id == credentials.org_id
    ).first()

    if not organization or not organization.is_active:
        raise HTTPException(
            status_code=403,
            detail="Organization inactive or not found"
        )

    encryption_key = os.getenv("API_SECRET_ENCRYPTION_KEY")

    if not encryption_key:
        raise HTTPException(
            status_code=500,
            detail="Encryption key not configured"
        )

    try:
        cipher = Fernet(encryption_key.encode())

        api_secret = cipher.decrypt(
            credentials.api_secret.encode()
        ).decode()

    except (InvalidToken, ValueError):
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt API secret"
        )

    message = "\n".join([
        timestamp,
        "POST",
        "/api/v1/remitters/",
        api_key,
        name,
        email,
        phone,
        document_type,
        document_number or "",
    ])

    expected_signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    return organization



@router.post("/")
async def create_remitter(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    document_type: str = Form(...),
    document_number: str = Form(""),

    document: UploadFile = File(...),

    api_key: str = Header(..., alias="X-API-KEY"),
    timestamp: str = Header(..., alias="X-TIMESTAMP"),
    signature: str = Header(..., alias="X-SIGNATURE"),

    db: Session = Depends(get_db)
):


    name = name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    document_type = document_type.strip()
    document_number = document_number.strip()


    if document.content_type != "image/jpeg":
        raise HTTPException(
            status_code=400,
            detail="Only JPEG images are allowed"
        )


    file_content = await document.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Document cannot be empty"
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 5 MB"
        )


    try:
        with Image.open(BytesIO(file_content)) as image:
            if image.format != "JPEG":
                raise HTTPException(
                    status_code=400,
                    detail="Only valid JPEG images are allowed"
                )
            image.verify()

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid JPEG image"
        )


    organization = authenticate_organization(
        api_key=api_key,
        timestamp=timestamp,
        signature=signature,
        name=name,
        email=email,
        phone=phone,
        document_type=document_type,
        document_number=document_number,
        db=db
    )


    existing_remitter = db.query(Remitter).filter(
        Remitter.org_id == organization.org_id,
        Remitter.email == email
    ).first()

    if existing_remitter:
        raise HTTPException(
            status_code=409,
            detail="Remitter already exists"
        )


    try:

        new_remitter = Remitter(
            org_id=organization.org_id,
            name=name,
            email=email,
            phone=phone,
            is_active=True
        )

        db.add(new_remitter)

        db.flush()
        new_document = RemitterDocument(
            remitter_id=new_remitter.remitter_id,
            document_type=document_type,
            document_number=document_number or None,
            document_data=file_content
        )

        db.add(new_document)


        db.commit()

        db.refresh(new_remitter)
        db.refresh(new_document)

        return {
            "message": "Remitter registered successfully",
            "remitter_id": new_remitter.remitter_id,
            "org_id": organization.org_id,
            "document_id": new_document.document_id
        }

    except HTTPException:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create remitter"
        )
