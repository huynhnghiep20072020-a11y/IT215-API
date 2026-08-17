import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("MEDCARE_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("Lỗi: Chưa cấu hình MEDCARE_SECRET_KEY trong file .env")

app = FastAPI(title="MedCare E-Prescription System")
security = HTTPBearer()

medical_db = {}

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ["doctor", "pharmacist"]:
            raise ValueError('Vai trò chỉ được phép là "doctor" hoặc "pharmacist"')
        return v

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/v1/medical/register", status_code=status.HTTP_201_CREATED)
def register(staff: RegisterRequest):
    if staff.username in medical_db:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại trên hệ thống")
    

    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(staff.password.encode('utf-8'), salt)
    

    medical_db[staff.username] = {
        "password": hashed_pwd,
        "role": staff.role
    }
    
    return {"message": "Đăng ký tài khoản nhân viên y tế thành công", "username": staff.username, "role": staff.role}

@app.post("/api/v1/medical/login")
def login(credentials: LoginRequest):
    user_record = medical_db.get(credentials.username)
    
    if not user_record or not bcrypt.checkpw(credentials.password.encode('utf-8'), user_record["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không chính xác"
        )
    
  
    now = datetime.now(timezone.utc)
    payload = {
        "sub": credentials.username,
        "role": user_record["role"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=20)).timestamp())
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "Bearer"}

def get_current_user_payload(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phiên làm việc đã hết hạn (Token Expired)")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chứng thư xác thực không hợp lệ (Invalid Token)")

def require_role(allowed_roles: list):
    def role_checker(payload: dict = Depends(get_current_user_payload)):
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền hạn thực hiện tác vụ này")
        return payload
    return role_checker


@app.post("/api/v1/prescriptions")
def create_prescription(current_user: dict = Depends(require_role(["doctor"]))):
    
    return {
        "message": "Ký và tạo đơn thuốc điện tử thành công",
        "doctor_name": current_user.get("sub"),
        "status": "CREATED"
    }

@app.get("/api/v1/prescriptions/view")
def view_prescription(current_user: dict = Depends(require_role(["doctor", "pharmacist"]))):

    return {
        "message": "Truy xuất hồ sơ đơn thuốc thành công",
        "requested_by": current_user.get("sub"),
        "role": current_user.get("role"),
        "data": "Nội dung đơn thuốc mật..."
    }