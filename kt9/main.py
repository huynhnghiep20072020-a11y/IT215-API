from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime, timezone
import routers

app = FastAPI()

def get_current_time_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    
    if isinstance(detail, dict) and "message" in detail and "error" in detail:
        message = detail["message"]
        error = detail["error"]
    else:
        message = str(detail)
        error = str(detail)
        
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": message,
            "data": None,
            "error": error,
            "timestamp": get_current_time_str(),
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Dữ liệu đầu vào không hợp lệ",
            "data": None,
            "error": exc.errors(),
            "timestamp": get_current_time_str(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Lỗi hệ thống nội bộ",
            "data": None,
            "error": str(exc),
            "timestamp": get_current_time_str(),
            "path": request.url.path
        }
    )

app.include_router(routers.router)