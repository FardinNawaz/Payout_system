import hashlib
import hmac
import time
from fastapi import Depends, HTTPException,Header,Request
from sqlalchemy.orm import Session
from database import get_db
from models import APICLIENT

async def verify_api_request(
        request:Request,
        x_api_key: str = Header(..., alias="X-API-KEY"),
        x_timestamp: str = Header(..., alias="X-TIMESTAMP"),
        x_signature: str = Header(..., alias="X-SIGNATURE"),
        db:Session=Depends(get_db)
):
    api_client=(db.query(APICLIENT)).filter(APICLIENT.api_key==x_api_key).first()
    if not api_client:
        raise HTTPException(
            status_code=401,
            detail="Invalid api key"
        )
    try:
        time_stamp=int(x_timestamp)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Timestamp"
        )
    if abs(int(time.time())-time_stamp) >300:
        raise HTTPException(
            status_code=401,
            detail="Request timestamp expired"
        )

    body = await request.body()

    message = (
        x_timestamp
        + request.method.upper()
        + request.url.path
        + body.decode("utf-8")
    )

  
    expected_signature = hmac.new(
        api_client.api_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected_signature,x_signature
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Signature"
        )

    return api_client
