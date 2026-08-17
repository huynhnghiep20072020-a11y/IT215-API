from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from app.models import User
from app.config import settings
from app.exceptions import AppException

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.TRUSTBANK_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AppException(401, "INVALID_TOKEN", "Token không hợp lệ hoặc giả mạo")
    except JWTError:
        raise AppException(401, "INVALID_TOKEN", "Token không hợp lệ, giả mạo hoặc hết hạn")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise AppException(401, "INVALID_TOKEN", "Tài khoản không tồn tại")
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise AppException(403, "PERMISSION_DENIED", "Bạn không có quyền quản trị viên")
    return current_user