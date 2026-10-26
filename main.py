
from fastapi import FastAPI, Request,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes.auth.auth import router as auth_router
from routes.admin.admin import router as admin_router
from routes.user_details.remitter import router as payment_details_router
from routes.user_details.user_doc import router as user_doc_router
from routes.user_details.beneficiary.beneficiary import router as beneficiay_payment
from routes.new import router as check_user
from routes.api_client.api_client import router as api_client_router
from routes.api_client.test_pi_client import router as test_api
from routes.payouts.payout import router as payout_router
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Payout System API",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)


app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(admin_router)
app.include_router(payment_details_router)
app.include_router(user_doc_router)
app.include_router(beneficiay_payment)
app.include_router(check_user)
app.include_router(api_client_router)
app.include_router(test_api)
app.include_router(payout_router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_ui_parameters={
            "persistAuthorization": True,
        },
    )



@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "message": "Invalid request data",
            "errors": [
                {
                    "field": str(error["loc"][-1]),
                    "message": error["msg"],
                }
                for error in exc.errors()
            ],
        },
    )