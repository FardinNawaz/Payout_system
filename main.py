
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes.auth.auth import router as auth_router
from routes.admin.admin import router as admin_router
from routes.user_details.remitter import router as payment_details_router
from routes.user_details.user_doc import router as user_doc_router


app = FastAPI(title="Payout System API")

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(admin_router)
app.include_router(payment_details_router)
app.include_router(user_doc_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={
            "message": "Invalid request data",
            "errors": [
                {
                    "field": ".".join(str(item) for item in error["loc"]),
                    "message": error["msg"],
                }
                for error in exc.errors()
            ],
        },
    )