import secrets
from sqlalchemy.orm import Session
from models import APICLIENT

def generate_api(
        db:Session,
        user_id:str,
):
    existing_client=db.query(APICLIENT).filter(APICLIENT.user_id==user_id).first()

    if existing_client:
        return existing_client,False

    api_key="lp+live_"+secrets.token_urlsafe(24)
    api_secret=secrets.token_urlsafe(48)


    api_client=APICLIENT(
        user_id=user_id,
        api_key=api_key,
        api_secret=api_secret
    )
    try:
        db.add(api_client)
        db.commit()
        db.refresh(api_client)

    except Exception:
        db.rollback()
        raise

    
    return api_client, True