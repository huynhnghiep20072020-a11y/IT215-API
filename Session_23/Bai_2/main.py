# 1. Lỗi điều kiện phân quyền trong require_admin()

# Vị trí lỗi: if current_user["role"] == "admin" or current_user["is_active"]:

# Giải thích: Việc sử dụng toán tử or khiến cho bất kỳ user nào đang hoạt động (is_active: True) cũng đều vượt qua được bước kiểm tra quyền admin. Lẽ ra hệ thống phải yêu cầu bắt buộc role là admin.

# Test case chứng minh: Test case 1 (User xóa khóa học). User với user-token có is_active = True, nên toán tử or trả về True,
# cho phép user gọi API DELETE /admin/courses/{course_id} thành công thay vì trả về 403 Forbidden.

# 2. Lỗi Middleware yêu cầu Authorization với mọi request & chặn OPTIONS

# Vị trí lỗi:

# Python
# if "authorization" not in request.headers:
#     return JSONResponse(status_code=401...)
# Giải thích: Middleware chặn tất cả các luồng request không có header Authorization. Điều này dẫn đến hai hậu quả nghiêm trọng:

# Trình duyệt gửi CORS preflight request (phương thức OPTIONS) không kèm token sẽ bị chặn đứng trước khi tới được CORSMiddleware.

# Endpoint công khai /health cũng bị bắt buộc phải có token.

# Test case chứng minh:

# Test case 2 (Kiểm tra trạng thái hệ thống): Gọi GET /health không có token trả về 401 Unauthorized thay vì 200 OK.

# Test case 3 (CORS preflight): Gửi request OPTIONS /courses bị Middleware chặn lại và trả về 401, khiến trình duyệt báo lỗi CORS.

# 3. Lỗi cấu hình CORS cho phép mọi nguồn truy cập

# Vị trí lỗi: allow_origins=["*"], allow_credentials=True trong CORSMiddleware.

# Giải thích: Sử dụng * để mở CORS cho mọi domain là một lỗ hổng bảo mật nghiêm trọng. Đặc biệt, theo đặc tả chuẩn của CORS, việc kết hợp allow_origins=["*"]
# và allow_credentials=True thường bị các trình duyệt hiện đại từ chối. 
# Hệ thống cũng đã vi phạm quy tắc chỉ cho phép hai Frontend cụ thể.

# Test case chứng minh: Test case 4 (Website không được phép). Gọi API từ [https://unknown-website.com](https://unknown-website.com) vẫn được hệ thống chấp nhận thay vì từ chối.


from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# SỬA LỖI 3: Giới hạn chính xác danh sách các origin được phép kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TOKENS = {
    "admin-token": {
        "username": "admin01",
        "role": "admin",
        "is_active": True,
    },
    "user-token": {
        "username": "student01",
        "role": "user",
        "is_active": True,
    },
    "locked-token": {
        "username": "locked01",
        "role": "user",
        "is_active": False,
    },
}


@app.middleware("http")
async def authentication_middleware(request, call_next):
    # SỬA LỖI 2: Bỏ qua kiểm tra Authorization với phương thức OPTIONS và endpoint public /health
    if request.method != "OPTIONS" and request.url.path != "/health":
        if "authorization" not in request.headers:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header is required"},
            )

    response = await call_next(request)
    response.headers["X-System-Name"] = "Learning Management System"
    return response


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = TOKENS.get(token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
        
    # BỔ SUNG LỖI LOGIC: Khóa tài khoản không cho phép truy cập API
    if not user.get("is_active"):
        raise HTTPException(
            status_code=403,
            detail="Inactive user account",
        )

    return user


def require_admin(current_user: dict = Depends(get_current_user)):
    # SỬA LỖI 1: Bắt buộc role phải là 'admin' 
    # (trạng thái is_active đã được kiểm tra ở get_current_user)
    if current_user.get("role") == "admin":
        return current_user

    raise HTTPException(
        status_code=403,
        detail="Admin permission required",
    )


@app.get("/health")
def health_check():
    return {"status": "UP"}


@app.get("/courses")
def get_courses(current_user: dict = Depends(get_current_user)):
    return {
        "items": [
            {"id": 1, "name": "FastAPI Basic"},
            {"id": 2, "name": "FastAPI Security"},
        ]
    }


@app.delete("/admin/courses/{course_id}")
def delete_course(
    course_id: int,
    current_user: dict = Depends(require_admin),
):
    return {
        "message": f"Course {course_id} has been deleted",
        "deleted_by": current_user["username"],
    }