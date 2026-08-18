# PHẦN A.
# PHÂN TÍCH INPUT/OUTPUT
# Để hệ thống hoạt động và phân quyền chính xác, cần xác định rõ các luồng dữ liệu:Dữ liệu có trong JWT (Input gián tiếp):
#     sub (username/user_id): Xác định danh tính người dùng.role: Vai trò (admin hoặc user).exp: Thời gian hết hạn của token.
#     Dữ liệu cần lấy từ hệ thống (State):Trạng thái hoạt động của tài khoản (có bị khóa hay không).Dữ liệu kết quả thi (thuộc về ai) 
#     để xử lý quyền sở hữu.Thông tin request cần dùng để phân quyền (Input trực tiếp):HTTP Method (GET, POST, PATCH, OPTIONS...).
#     Đường dẫn (URL Path).Path parameter (VD: exam_id, username hoặc user_id trên URL) để so sánh quyền sở hữu.Header Authorization.
#     Kết quả khi được phép truy cập:HTTP Status 200 OK hoặc 201 Created.Dữ liệu JSON tương ứng với yêu cầu.Kết quả khi token hoặc quyền không hợp lệ:
#         HTTP Status 401 Unauthorized: Lỗi xác thực (Không có token, token sai, token hết hạn).HTTP Status 403 Forbidden: Lỗi phân quyền 
#         (Có token hợp lệ nhưng role không đủ, tài khoản bị khóa, hoặc vi phạm quyền sở hữu dữ liệu - IDOR).PHẦN B. ĐỀ XUẤT CÁC GIẢI PHÁPGiải pháp 1:
#             Sử dụng Dependency tại từng endpoint (FastAPI Native)Sử dụng Depends() của FastAPI để tiêm logic xác thực và phân quyền vào từng endpoint.
#             Cách làm: Khai báo hàm get_current_user để giải mã JWT, và hàm require_admin để kiểm tra role. Gắn chúng vào tham số của các hàm xử lý API.
#             Ưu điểm: Code gắn chặt với API, xử lý Path Parameter và IDOR cực kỳ dễ dàng.Nhược điểm: Dễ mắc Bẫy 3 (Quên gắn dependency khi tạo API mới).
#             Giải pháp 2: Sử dụng Authorization MiddlewareBắt mọi request đi qua một Middleware. Middleware giải mã JWT, đọc URL và Method, đối chiếu với một từ điển PROTECTED_ROUTES.
#             Cách làm: Viết hàm @app.middleware("http"), parse chuỗi request URL.Ưu điểm: Tập trung tại một nơi, không sợ quên (Giết chết Bẫy 3).
#             Nhược điểm: Mắc Bẫy 1 (Khó xử lý regex cho path parameter /exams/10/lock), mắc Bẫy 2 (phải tự viết logic loại trừ OPTIONS), 
#             và mắc Bẫy 4 (Middleware rất khó biết resource đó thuộc về user nào để chặn).Giải pháp 3: Phương án kết hợp (Hybrid - Tối ưu nhất)
#             Tầng Middleware/Global: Chỉ xử lý CORS (bỏ qua OPTIONS) và bóc tách token hợp lệ cơ bản.Tầng Router Dependency (Nhóm Endpoint):
#                 Thay vì gắn Dependency từng endpoint, ta gom nhóm các API của admin vào một APIRouter và gắn Depends(require_admin) cho toàn bộ router đó.
#                 Tầng Endpoint Dependency: Xử lý các logic phức tạp như quyền sở hữu dữ liệu (IDOR - Bẫy 4).PHẦN C. SO SÁNH VÀ LỰA CHỌNBảng so sánhTiêu chí
#                 Giải pháp 1: DependencyGiải pháp 2: MiddlewareGiải pháp 3: Kết hợp (Router Dep + Endpoint Dep)Dễ đọc codeCao (Rõ ràng tại từng hàm)
#                 Trung bình (Bảng phân quyền lớn dễ rối)Rất cao (Tách bạch logic)Khả năng tái sử dụngRất caoTrung bìnhRất caoNguy cơ bỏ sót (Bẫy 3)
#                 CaoRất thấp (Mặc định chặn)Rất thấp (Nhóm theo Router)Xử lý path parameter (Bẫy 1)Rất tốt (Tự động bóc tách)Yếu (Cần dùng Regex phức tạp)
#                 Rất tốtXử lý CORS (Bẫy 2)Tốt (Không can thiệp)Kém (Dễ chặn nhầm OPTIONS)Tốt (Giao cho CORSMiddleware)Kiểm tra quyền sở hữu (Bẫy 4)Rất tốt
#                 Rất khó / Không thểRất tốtKhả năng kiểm thửDễ (Unit test từng dependency)Khó (Phải test qua giao thức HTTP)DễKhả năng bảo trìKháKém khi route phức tạp
#                 Tốt nhấtHiệu năngNhanhChậm (parse regex liên tục)NhanhLựa chọn và Giải thích:Lựa chọn: Giải pháp 3 (Kết hợp sử dụng Router Dependencies và Endpoint Dependencies).
#                 Lý do: Giải pháp này tận dụng sức mạnh Dependency Injection của FastAPI. Bằng cách gom tất cả API bắt đầu bằng /admin vào một APIRouter và áp dụng Dependency cấp router,
#                 ta loại bỏ hoàn toàn Bẫy 3. Đồng thời, vì vẫn dùng Dependency, ta dễ dàng truy cập Path Parameters để giải quyết Bẫy 1 và Bẫy 4 (IDOR) mà Middleware thuần túy không làm được.
#                 Trường hợp không nên sử dụng: Hệ thống legacy (cũ) không dùng FastAPI, hoặc hệ thống API Gateway trung tâm nơi việc phân quyền được đẩy ra một service khác độc lập (như Kong/Tyk) 
#                 chỉ dựa trên cấu hình URL regex.PHẦN D. THIẾT KẾ VÀ TRIỂN KHAI1. Luồng xử lý (Lưu đồ tóm tắt)Client gửi Request.CORSMiddleware can thiệp:Nếu là OPTIONS: Trả về 200 OK (Giải quyết Bẫy 2).
#                 Request đi vào Router:Nếu là /health: Trực tiếp trả về 200 OK.Nếu là /admin/*: Tự động đi qua require_admin (Giải quyết Bẫy 3 & Bẫy 1).Nếu là /users/{username}/results:
#                     Đi qua logic kiểm tra username có khớp với token không (Giải quyết Bẫy 4).Dependency giải mã Token:Nếu lỗi/hết hạn -> Bắn lỗi 401.Nếu không đủ role -> Bắn lỗi 403.Endpoint xử lý logic và trả về kết quả.

from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, APIRouter, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError

app = FastAPI()

# BẪY 2: Cấu hình CORS xử lý Request OPTIONS một cách tự động
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "exam-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dữ liệu Mock
USERS_DB = {
    "admin01": {"username": "admin01", "role": "admin", "is_active": True},
    "student01": {"username": "student01", "role": "user", "is_active": True},
    "student02": {"username": "student02", "role": "user", "is_active": True},
}

RESULTS_DB = {
    "student01": [{"exam": "Toan", "score": 9}],
    "student02": [{"exam": "Ly", "score": 8}],
}

# --- DEPENDENCIES CHUNG ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    
    user = USERS_DB.get(username)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=403, detail="User not found or locked")
    return user

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user


# --- ROUTER CHO ADMIN (Giải quyết BẪY 3 & BẪY 1) ---
# Tự động áp dụng require_admin cho mọi API thuộc router này
admin_router = APIRouter(
    prefix="/admin", 
    tags=["Admin"], 
    dependencies=[Depends(require_admin)]
)

@admin_router.post("/exams")
def create_exam():
    return {"msg": "Exam created"}

# Giải quyết BẪY 1: Path parameter được xử lý tự nhiên, không sợ lỗi Regex
@admin_router.patch("/exams/{exam_id}/lock")
def lock_exam(exam_id: int):
    return {"msg": f"Exam {exam_id} locked"}

@admin_router.get("/results")
def get_all_results():
    return RESULTS_DB


# --- ROUTER CHO USER CHUNG ---
user_router = APIRouter(tags=["Users"])

@user_router.get("/exams")
def view_exams(current_user: dict = Depends(get_current_user)):
    return [{"exam": "Toan", "time": "08:00"}, {"exam": "Ly", "time": "10:00"}]

# Giải quyết BẪY 4: Kiểm tra IDOR - User truy cập chéo tài nguyên
@user_router.get("/users/{username}/results")
def get_my_results(
    username: str = Path(...), 
    current_user: dict = Depends(get_current_user)
):
    # Admin có thể xem của ai cũng được, User chỉ xem được của mình
    if current_user["role"] != "admin" and current_user["username"] != username:
        raise HTTPException(status_code=403, detail="Not allowed to view others' results")
    
    return RESULTS_DB.get(username, [])

@user_router.get("/users/me/results")
def get_me_results(current_user: dict = Depends(get_current_user)):
    return RESULTS_DB.get(current_user["username"], [])


# --- PUBLIC API ---
@app.get("/health", tags=["Public"])
def health_check():
    return {"status": "UP"}


# Đăng ký Routers vào App
app.include_router(admin_router)
app.include_router(user_router)


# --- API TẠO TOKEN ĐỂ TEST ---
@app.get("/issue-token/{username}")
def get_token(username: str):
    if username not in USERS_DB:
        return {"error": "User not found"}
    user = USERS_DB[username]
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = jwt.encode(
        {"sub": user["username"], "role": user["role"], "exp": expires_at},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token}