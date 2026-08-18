from fastapi import FastAPI, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

app = FastAPI(title="FlashMove Delivery System")

# ==========================================
# PHẦN 4: CẤU HÌNH CORS WHITELIST ĐA DOMAIN
# ==========================================
# Khai báo chính xác 2 domain được phép truy cập
ALLOWED_ORIGINS = [
    "https://driver.flashmove.io",
    "https://hub.flashmove.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,           # Chỉ chấp nhận từ 2 domain này
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],  # Chỉ cho phép GET, POST, PATCH
    allow_headers=["Content-Type", "X-Role-Identity"], # Chỉ cho phép 2 headers này
)

# ==========================================
# PHẦN 1 & 2: HỆ THỐNG VAI TRÒ & LỚP CHẶN TẬP TRUNG
# ==========================================

# 1. Định nghĩa Exception tùy chỉnh để trả về đúng cấu trúc JSON yêu cầu
class UnauthorizedRoleException(Exception):
    pass

@app.exception_handler(UnauthorizedRoleException)
async def unauthorized_role_handler(request: Request, exc: UnauthorizedRoleException):
    return JSONResponse(
        status_code=403,
        content={"status": "Rejected", "reason": "Unauthorized action for this role"},
    )

# 2. Xây dựng lớp bảo vệ tập trung (Dependency)
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    # Hàm __call__ biến class này thành một Dependency tự động chạy khi request đi tới
    def __call__(self, x_role_identity: str = Header(default=None)):
        # Kiểm tra Role có tồn tại và có nằm trong danh sách được phép hay không
        if not x_role_identity or x_role_identity.upper() not in self.allowed_roles:
            raise UnauthorizedRoleException()
        return x_role_identity.upper()

# 3. Phân tầng quyền hạn (Tạo các chốt chặn tái sử dụng)
REQUIRE_DISPATCHER = RoleChecker(["DISPATCHER"])
REQUIRE_DISPATCHER_DRIVER = RoleChecker(["DISPATCHER", "DRIVER"])
REQUIRE_ALL_ROLES = RoleChecker(["DISPATCHER", "DRIVER", "CUSTOMER_SUPPORT"])

# ==========================================
# PHẦN 3: THIẾT LẬP CÁC API ENDPOINTS
# ==========================================

@app.post("/api/v1/orders/assign", dependencies=[Depends(REQUIRE_DISPATCHER)])
async def assign_order():
    """Chỉ duy nhất DISPATCHER được phép gọi"""
    return {"status": "Success", "data": "Order has been assigned successfully."}

@app.patch("/api/v1/orders/status", dependencies=[Depends(REQUIRE_DISPATCHER_DRIVER)])
async def update_order_status():
    """Chỉ cho phép DISPATCHER và DRIVER được gọi"""
    return {"status": "Success", "data": "Order status updated."}

@app.get("/api/v1/orders/track", dependencies=[Depends(REQUIRE_ALL_ROLES)])
async def track_order():
    """Cả 3 vai trò đều có quyền truy cập"""
    return {"status": "Success", "data": "Real-time tracking data."}