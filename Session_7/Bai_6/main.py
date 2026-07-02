from fastapi import FastAPI, status, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

# --- Dữ liệu nội bộ ---
promo_codes_db = {
    "SUMMER25": {"code": "SUMMER25", "discount_rate": 0.15, "max_budget": 50000000, "is_active": True},
    "WELCOME50": {"code": "WELCOME50", "discount_rate": 0.50, "max_budget": 10000000, "is_active": False}
}

class PromoInternal(BaseModel):
    code: str
    discount_rate: float
    max_budget: int
    is_active: bool

# --- 1. Thiết kế Schema Public ---
class PromoPublic(BaseModel):
    code: str
    discount_rate: float

# --- 3. Cấu hình Bộ lọc phản hồi lỗi tập trung (Global Exception Handler) ---
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "data": None,
            "error": exc.detail,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

# --- 2. Triển khai Endpoint tra cứu ---
@app.get("/promos/{code}", response_model=PromoPublic, status_code=status.HTTP_200_OK)
def get_promo_code(code: str):
    if code not in promo_codes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mã giảm giá không tồn tại"
        )
        
    promo = promo_codes_db[code]
    
    if not promo["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã giảm giá đã hết hạn sử dụng"
        )
        
    return promo