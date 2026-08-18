import time
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import BaseModel

# -----------------------------
# CẤU HÌNH CƠ BẢN VÀ LOGGING
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("LMS_Logger")

app = FastAPI(title="LMS Resources API")

SECRET_KEY = "my_super_secret_key_for_training"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# -----------------------------
# CẤU HÌNH CORS
# -----------------------------
# Cấu hình chặn tất cả ngoại trừ localhost:3000 và localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# CUSTOM MIDDLEWARE
# -----------------------------
@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    req_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Thực thi các middleware và router phía sau (Bao gồm CORS, Auth, v.v...)
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Thêm Headers
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Process-Time"] = str(process_time)
    
    # Ghi Log
    logger.info(
        f"Request ID: {req_id} | Method: {request.method} | "
        f"Path: {request.url.path} | Status: {response.status_code} | "
        f"Process Time: {process_time:.4f}s"
    )
    
    return response

# -----------------------------
# DỮ LIỆU MẪU (MOCK DATABASE)
# -----------------------------
users = {
    "admin01": {"username": "admin01", "password": "123456", "role": "admin", "is_active": True},
    "student01": {"username": "student01", "password": "123456", "role": "user", "is_active": True},
    "student02": {"username": "student02", "password": "123456", "role": "user", "is_active": False},
}

resources_db = {
    1: {"id": 1, "title": "JWT Authorization", "description": "Tài liệu hướng dẫn JWT", "url": "https://example.com/jwt.pdf", "is_published": True, "created_by": "admin01"},
    2: {"id": 2, "title": "CORS Basic", "description": "Cấu hình CORS trong FastAPI", "url": "https://example.com/cors.pdf", "is_published": False, "created_by": "admin01"}
}
resource_id_counter = 2

# Models (Pydantic)
class ResourceCreate(BaseModel):
    title: str
    description: str
    url: str

class ResourceResponse(BaseModel):
    id: int
    title: str
    description: str
    url: str
    is_published: bool
    created_by: str

# -----------------------------
# PHẦN AUTHENTICATION & DEPENDENCIES
# -----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Tự động kiểm tra tính hợp lệ và thời hạn (Bẫy 3)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Kiểm tra user tồn tại trong hệ thống (Bẫy 2: Xác thực role theo DB thay vì token)
    user = users.get(username)
    if user is None:
        raise credentials_exception
        
    # Bẫy 1: Khóa tài khoản sau khi token đã cấp
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
        
    return user

def require_admin(current_user: dict = Depends(get_current_user)):
    # Phân quyền từ DB thay vì Payload Token
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    return current_user

# -----------------------------
# API ROUTERS
# -----------------------------

@app.get("/health", tags=["Public"])
def health_check():
    return {"status": "UP"}

@app.post("/auth/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.get(form_data.username)
    # Sai user hoặc mật khẩu
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    # User bị khóa đăng nhập
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Inactive user account")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", tags=["Users"])
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

@app.get("/resources", response_model=List[ResourceResponse], tags=["Resources"])
def list_resources(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        # Admin xem tất cả
        return list(resources_db.values())
    else:
        # User chỉ xem cái đã publish
        return [r for r in resources_db.values() if r["is_published"]]

@app.get("/resources/{resource_id}", response_model=ResourceResponse, tags=["Resources"])
def get_resource(resource_id: int, current_user: dict = Depends(get_current_user)):
    resource = resources_db.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    # Bẫy 5: User truy cập tài nguyên ẩn -> 404 để giấu sự tồn tại
    if not resource["is_published"] and current_user["role"] != "admin":
        raise HTTPException(status_code=404, detail="Resource not found")
        
    return resource

@app.post("/resources", response_model=ResourceResponse, tags=["Resources (Admin)"])
def create_resource(
    res_data: ResourceCreate, 
    current_user: dict = Depends(require_admin)
):
    global resource_id_counter
    resource_id_counter += 1
    new_resource = {
        "id": resource_id_counter,
        "title": res_data.title,
        "description": res_data.description,
        "url": res_data.url,
        "is_published": False, # Mặc định là false khi mới tạo
        "created_by": current_user["username"]
    }
    resources_db[resource_id_counter] = new_resource
    return new_resource

@app.patch("/resources/{resource_id}/publish", tags=["Resources (Admin)"])
def publish_resource(
    resource_id: int, 
    current_user: dict = Depends(require_admin)
):
    resource = resources_db.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource["is_published"] = True
    return {"message": "Resource has been published", "resource": resource}

@app.delete("/resources/{resource_id}", tags=["Resources (Admin)"])
def delete_resource(
    resource_id: int, 
    current_user: dict = Depends(require_admin)
):
    resource = resources_db.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    del resources_db[resource_id]
    return {"message": f"Resource {resource_id} deleted successfully"}