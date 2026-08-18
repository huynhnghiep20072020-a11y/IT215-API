from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MegaMart ERP Backend")

# ==========================================
# 1. CẤU HÌNH CORS NGHIÊM NGẶT
# ==========================================
# Tuyệt đối không dùng ["*"]. Chỉ cho phép domain frontend chính thức.
ALLOWED_ORIGINS = [
    "https://internal.megamart.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"], # Chỉ cho phép GET, POST
    allow_headers=["Content-Type", "X-User-Role"], # Chỉ cho phép các header cụ thể
)

# ==========================================
# 2. THIẾT LẬP HỆ THỐNG VAI TRÒ & PHÂN QUYỀN
# ==========================================
# Định nghĩa các route và quyền hạn tương ứng
PROTECTED_ROUTES = {
    "/api/v1/salary/modify": ["ADMIN", "HR"],
    "/api/v1/system/settings": ["ADMIN"],
    "/api/v1/profile": ["ADMIN", "HR", "STAFF"]
}

# Custom Middleware Phân quyền tập trung
@app.middleware("http")
async def rbac_middleware(request: Request, call_next):
    path = request.url.path
    
    # Kiểm tra xem route có nằm trong danh sách cần bảo vệ không
    if path in PROTECTED_ROUTES:
        # Bóc tách vai trò từ Header (Mặc định là rỗng nếu không truyền)
        user_role = request.headers.get("X-User-Role", "").upper()
        
        # Lấy danh sách vai trò được phép truy cập route này
        allowed_roles = PROTECTED_ROUTES[path]
        
        # Nếu vai trò không hợp lệ -> Chặn đứng và trả về 403
        if user_role not in allowed_roles:
            return JSONResponse(
                status_code=403, 
                content={"error": "Permission Denied"}
            )
            
    # Nếu hợp lệ hoặc route không cần bảo vệ -> Cho request đi tiếp vào Controller
    response = await call_next(request)
    return response




from fastapi import FastAPI, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

app = FastAPI(title="MegaMart ERP Backend")

# ==========================================
# PHẦN 4: CẤU HÌNH CORS NGHIÊM NGẶT
# ==========================================
# Thay vì dùng allow_origins=["*"], ta chỉ định đích danh domain hợp lệ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["[https://internal.megamart.com](https://internal.megamart.com)"], # Chỉ cho phép Frontend nội bộ
    allow_credentials=True,
    allow_methods=["GET", "POST"],                   # Chỉ cho phép GET và POST
    allow_headers=["Content-Type", "X-User-Role"],   # Chỉ cho phép các headers chỉ định
)


# ==========================================
# PHẦN 1 & 2: HỆ THỐNG VAI TRÒ & PHÂN QUYỀN
# ==========================================

# Định nghĩa Custom Exception để trả về đúng format JSON yêu cầu khi lỗi
class PermissionDeniedException(Exception):
    pass

@app.exception_handler(PermissionDeniedException)
async def permission_denied_handler(request: Request, exc: PermissionDeniedException):
    return JSONResponse(
        status_code=403,
        content={"error": "Permission Denied"},
    )

# Dependency tập trung: Kiểm tra quyền truy cập (RBAC)
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    # Hàm __call__ giúp class này hoạt động như một Dependency trong FastAPI
    def __call__(self, x_user_role: str = Header(default=None)):
        # Nếu không có header X-User-Role hoặc Role không nằm trong danh sách cho phép
        if not x_user_role or x_user_role not in self.allowed_roles:
            raise PermissionDeniedException()
        return x_user_role

# Khởi tạo các nhóm quyền để tái sử dụng
ADMIN_ONLY = RoleChecker(["ADMIN"])
ADMIN_AND_HR = RoleChecker(["ADMIN", "HR"])
ALL_ROLES = RoleChecker(["ADMIN", "HR", "STAFF"])


# ==========================================
# PHẦN 3: CÁC API ENDPOINT THỬ NGHIỆM
# ==========================================

@app.get("/api/v1/salary/modify", dependencies=[Depends(ADMIN_AND_HR)])
async def modify_salary():
    """Chỉ cho phép vai trò ADMIN và HR"""
    return {"message": "Success: Access granted to Salary data."}

@app.get("/api/v1/system/settings", dependencies=[Depends(ADMIN_ONLY)])
async def system_settings():
    """Chỉ duy nhất vai trò ADMIN được truy cập"""
    return {"message": "Success: Access granted to System Settings."}

@app.get("/api/v1/profile", dependencies=[Depends(ALL_ROLES)])
async def get_profile():
    """Cả 3 vai trò ADMIN, HR, STAFF đều truy cập được"""
    return {"message": "Success: Access granted to Personal Profile."}