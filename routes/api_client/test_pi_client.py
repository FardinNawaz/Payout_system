from fastapi import APIRouter, Depends
from models import APICLIENT
from services.api_auth import verify_api_request

router = APIRouter(prefix="/api/v1", tags=["API Authentication"])


@router.get("/test-auth")
async def test_auth(
    api_client: APICLIENT = Depends(verify_api_request)
):
    return {
        "message": "API authentication successful",
        "user_id": api_client.user_id
    }