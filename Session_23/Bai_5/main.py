from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.request_middleware import ProcessTimeMiddleware
from routers import auth_router, assignment_router, submission_router
from core.config import ALLOWED_ORIGIN

app = FastAPI(title="EduAssign API")

# 1. Cấu hình CORS - Không dùng "*" khi cho phép Credentials. Bỏ qua chặn OPTIONS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Cấu hình Custom Middleware đo thời gian, cấp Request ID
app.add_middleware(ProcessTimeMiddleware)

# 3. Đăng ký Routers
app.include_router(auth_router.router)
app.include_router(assignment_router.router)
app.include_router(submission_router.router)

# 4. Public Endpoint Health
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "UP"}