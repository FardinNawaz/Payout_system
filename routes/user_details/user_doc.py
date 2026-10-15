
import jwt

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User, DOCUMENT
from routes.user_details.user_doc_model import (
    DocumentDetail,
    DocumentData,
    Document_Response,
)
from routes.auth.auth import SECRET_KEY


router = APIRouter(
    prefix="/api/v1/user",
    tags=["User Documents"],
)


@router.post(
    "/document",
    response_model=Document_Response,
    status_code=201,
)
def add_document(
    data: DocumentDetail,
    access_token: str = Header(),
    db: Session = Depends(get_db),
):
    # 1. Verify JWT
    try:
        payload = jwt.decode(
            access_token.strip(),
            SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    # 2. Extract email from JWT
    email = payload.get("email")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )

    # 3. Find user
    user = (
        db.query(User)
        .filter(User.email == email.lower())
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    # 4. Check user role
    if user.role != "USER":
        raise HTTPException(
            status_code=403,
            detail="Only USER role can add documents",
        )

    # 5. Create document
    document = DOCUMENT(
        user_id=user.user_id,
        document_name=data.document_name,
        document_number=data.document_number,
        document_pic_url=data.document_pic_url,
    )

    # 6. Save document
    try:
        db.add(document)
        db.commit()
        db.refresh(document)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Document already registered or violates a database constraint",
        )

    # 7. Return nested response
    return Document_Response(
        message="Document added successfully",
        data=DocumentData(
            document_id=str(document.document_id),
            user_id=str(document.user_id),
            document_name=document.document_name,
        ),
    )
