
import hashlib
import hmac
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import APICLIENT

router = APIRouter(
    prefix="/api/v1/dev",
    tags=["Local Swagger Testing"],
)


class SignRequest(BaseModel):
    api_key: str
    method: str
    path: str
    body: str = ""


@router.post("/sign-request")
def sign_request(
    data: SignRequest,
    db: Session = Depends(get_db),
):
    api_client = (
        db.query(APICLIENT)
        .filter(APICLIENT.api_key == data.api_key)
        .first()
    )

    if not api_client:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    timestamp = str(int(time.time()))

    message = (
        timestamp
        + data.method.upper()
        + data.path
        + data.body
    )

    signature = hmac.new(
        api_client.api_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return {
        "X-API-KEY": api_client.api_key,
        "X-TIMESTAMP": timestamp,
        "X-SIGNATURE": signature,
    }
