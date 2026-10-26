from fastapi import APIRouter , Depends,Header,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schema.api_client import generate_api
from routes.admin.admin import check_admin

router=APIRouter(
    prefix="/api/v1/user",
    tags=["Admin Api"]
)

@router.post("/{user_id}/api-credentials")
def create_api_credentials(
    user_id:str,
    access_token:str=Header(),
    db:Session = Depends(get_db)
):
    check_admin(access_token,db)

    user=db.query(User).filter(User.user_id==user_id).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not Found"
        )
    try:
        api_client, created = generate_api(
            db=db,
            user_id=user_id
        )
    except Exception:
        db.rollback()
        raise

    if created:
        return {
            "message": "API credentials generated successfully",
            "user_id": user.user_id,
            "email": user.email,
            "api_key": api_client.api_key,
            "api_secret": api_client.api_secret
        }

    return {
        "message": "API credentials already exist",
        "user_id": user.user_id,
        "email": user.email,
        "api_key": api_client.api_key,
        "api_secret": None
    }