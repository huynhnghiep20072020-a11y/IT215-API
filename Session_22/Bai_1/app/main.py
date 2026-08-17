from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.database import engine, Base
from app.exceptions import AppException
from app.routers import auth, account, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrustBank Digital API")

app.include_router(auth.router)
app.include_router(account.router)
app.include_router(admin.router)

#  Bắt lỗi Custom App Exception
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )

#  Bắt lỗi Validation Pydantic / Input sai định dạng
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "VALIDATION_ERROR", "detail": "Dữ liệu đầu vào sai định dạng"},
    )

#  Bắt lỗi hệ thống chưa được kiểm soát Bảo vệ stack trace
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_SERVER_ERROR", "detail": "Lỗi máy chủ không xác định trước"},
    )