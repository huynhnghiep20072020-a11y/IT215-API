"""
Phần 1: Luồng dữ liệu

Khi Client gửi Request, nếu xử lý thành công, API sẽ đóng gói kết quả thành JSON chuẩn 6 trường trả về cho Frontend.

Nếu xảy ra lỗi, luồng thực thi tại Router lập tức bị ngắt. Lúc này, cơ chế Global Handler (@app.exception_handler) sẽ đứng ra bắt các ngoại lệ.

Dựa vào loại lỗi (RequestValidationError, HTTPException hay Exception), hệ thống sẽ tự động gán HTTP Status Code tương ứng,
thu thập thông tin lỗi (error, message), lấy thời gian thực (timestamp) và đường dẫn đang truy cập (path). 
Cuối cùng, bọc tất cả lại thành cấu trúc chuẩn 6 trường (Unified Envelope) và trả về,
đảm bảo phía giao diện luôn nhận được một khuôn mẫu thống nhất dù API thành công hay thất bại.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import routers

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Dữ liệu đầu vào không hợp lệ",
            "data": None,
            "error": exc.errors(),
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": exc.detail,
            "data": None,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
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
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

app.include_router(routers.router)