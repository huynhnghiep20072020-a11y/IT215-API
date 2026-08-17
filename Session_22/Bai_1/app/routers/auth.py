from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import schemas, models, security, exceptions
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", status_code=201, response_model=schemas.UserResponse)
def register(request: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        new_user = models.User(
            username=request.username,
            hashed_password=security.get_password_hash(request.password),
            role=request.role if request.role in ["customer", "admin"] else "customer"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise exceptions.AppException(409, "USER_ALREADY_EXISTS", "Username đã tồn tại")

@router.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not security.verify_password(request.password, user.hashed_password):
        raise exceptions.AppException(401, "INVALID_CREDENTIALS", "Sai tên đăng nhập hoặc mật khẩu")
    
    access_token = security.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password")
def change_password(request: schemas.ChangePasswordRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not security.verify_password(request.old_password, current_user.hashed_password):
        raise exceptions.AppException(401, "INVALID_CREDENTIALS", "Mật khẩu cũ không chính xác")
    
    if request.old_password == request.new_password:
        raise exceptions.AppException(400, "VALIDATION_ERROR", "Mật khẩu mới không được trùng mật khẩu cũ")
    
    current_user.hashed_password = security.get_password_hash(request.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}