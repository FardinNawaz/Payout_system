
from fastapi import FastAPI, Request,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes.auth.auth import router as auth_router
from routes.admin.admin import router as admin_router
# from routes.user_details.beneficiary.beneficiary import router as beneficiay_payment
from routes.organization.organization import router as create_organization
from routes.organization.users.organization_user import router as organization_user_router
from routes.remitter.remitter import router as org_remitter
from routes.organization.auth.organization_auth import router as auth_organiation
from routes.organization.beneficiary.beneficiary import router as org_beneficiary
from routes.payouts.payout import router as create_payout


app = FastAPI(
    title="Payout System API",
)


app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(admin_router)
app.include_router(create_organization)
app.include_router(organization_user_router)
app.include_router(org_remitter)
app.include_router( auth_organiation)
app.include_router(org_beneficiary)
app.include_router(create_payout)


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