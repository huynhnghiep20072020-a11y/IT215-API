import re
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


SECRET_KEY = "day_la_khoa_bi_mat_rat_an_toan_cua_ban"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Hệ thống quản lý sinh viên - Auth API")
security = HTTPBearer()


users_db = {}
user_id_counter = 1


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_minutes: int = 30) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ hoa')
        if not re.search(r"[a-z]", v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ thường')
        if not re.search(r"\d", v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ số')
        return v

class UserResponseData(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

class RegisterResponse(BaseModel):
    message: str
    data: UserResponseData

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
      
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc sai chữ ký")
    

    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Tài khoản đã bị khóa")
        
    return user



@app.post("/auth/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    global user_id_counter
   
    for user in users_db.values():
        if user["email"] == request.email:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng")
            
  
    hashed_pwd = hash_password(request.password)
    
    new_user = {
        "id": user_id_counter,
        "email": request.email,
        "full_name": request.full_name,
        "hashed_password": hashed_pwd,
        "role": "student",
        "is_active": True
    }
    
    users_db[user_id_counter] = new_user
    user_id_counter += 1
    
    return {
        "message": "Đăng ký tài khoản thành công",
        "data": new_user
    }

@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    
    user = next((u for u in users_db.values() if u["email"] == request.email), None)
    
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")
   
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Tài khoản của bạn đã bị khóa")
        
    
    token_data = {
        "sub": user["email"],
        "user_id": user["id"],
        "role": user["role"]
    }
    token = create_access_token(data=token_data, expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/auth/me", response_model=UserResponseData)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user