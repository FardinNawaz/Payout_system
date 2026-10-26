from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from routes.model import Usercheck

router =APIRouter(
    prefix='/user',
    tags=["Usercheck"]
)
@router.post("/check")
def check_user(
    data:Usercheck,
    db:Session=Depends(get_db)
):
    user=db.query(User).filter(User.email==data.email.lower()).first()

    if user:
        return {
            'message':'hii'
        }
    raise HTTPException(
        status_code=401,
        detail="User not exist"
    )