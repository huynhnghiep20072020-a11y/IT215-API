from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import enum

# ==========================================
# 1. CẤU HÌNH DATABASE
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/hospital_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. ĐỊNH NGHĨA MODEL DATABASE (Bảng medical_devices)
# ==========================================
# Sử dụng Enum của Python để đồng bộ với kiểu ENUM của MySQL
class DeviceStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

class MedicalDeviceModel(Base):
    __tablename__ = "medical_devices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_code = Column(String(50), unique=True, nullable=False)
    device_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.ACTIVE)

# Tự động tạo bảng nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SCHEMA XÁC THỰC INPUT/OUTPUT (PYDANTIC)
# ==========================================
class MedicalDeviceCreate(BaseModel):
    # Ràng buộc không rỗng
    device_code: str = Field(..., min_length=1, description="Mã thiết bị")
    # Ràng buộc tên tối thiểu 3 ký tự
    device_name: str = Field(..., min_length=3, description="Tên thiết bị")
    # Ràng buộc khoa phòng không rỗng
    department: str = Field(..., min_length=1, description="Khoa/Phòng sử dụng")
    # Sử dụng Literal để ép Client chỉ được gửi 1 trong 2 giá trị này
    status: Literal['ACTIVE', 'INACTIVE'] = Field(default='ACTIVE', description="Trạng thái")

class MedicalDeviceResponse(BaseModel):
    id: int
    device_code: str
    device_name: str
    department: str
    status: str

    class Config:
        from_attributes = True

app = FastAPI(title="Hệ Thống Quản Lý Thiết Bị Y Tế")

# ==========================================
# 4. TIỆN ÍCH BỌC DỮ LIỆU & BẮT LỖI (6 TRƯỜNG)
# ==========================================
def format_response(status_code: int, message: str, data: dict | list | None, path: str, error: str = None):
    """Hàm chuẩn hóa phản hồi API về đúng 6 trường quy chuẩn"""
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Middleware chặn Stack Trace, format lỗi 400, 404, 500 thành cấu trúc 6 trường"""
    error_str = "Not Found" if exc.status_code == 404 else "Bad Request" if exc.status_code == 400 else "Internal Error"
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_response(
            status_code=exc.status_code,
            message=exc.detail,
            data=None,
            path=request.url.path,
            error=error_str
        )
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 5. CÁC API NGHIỆP VỤ
# ==========================================

# [POST] Thêm thiết bị y tế mới
@app.post("/devices", status_code=status.HTTP_201_CREATED)
def create_medical_device(
    payload: MedicalDeviceCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    new_device = MedicalDeviceModel(
        device_code=payload.device_code,
        device_name=payload.device_name,
        department=payload.department,
        status=payload.status
    )
    
    # Bọc khối lệnh trong try...except để đảm bảo an toàn giao dịch (Transaction)
    try:
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        # Parse Pydantic model sang Dictionary để cho vào trường "data"
        data_response = MedicalDeviceResponse.model_validate(new_device).model_dump()
        
        return format_response(
            status_code=201,
            message="Thêm thiết bị y tế thành công",
            data=data_response,
            path=request.url.path
        )
        
    except IntegrityError:
        # Bắt bẫy dữ liệu: Xung đột mã thiết bị (Unique Constraint)
        db.rollback() # Bắt buộc phải hoàn tác để MySQL giải phóng connection
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Mã thiết bị đã tồn tại trên hệ thống"
        )
    except Exception:
        # Bắt các lỗi nghẽn mạch hoặc lỗi không xác định
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Xảy ra lỗi hệ thống khi lưu dữ liệu thiết bị"
        )

# [GET] Lấy danh sách toàn bộ thiết bị y tế
@app.get("/devices", status_code=status.HTTP_200_OK)
def get_all_devices(request: Request, db: Session = Depends(get_db)):
    devices = db.query(MedicalDeviceModel).all()
    
    # Serialize danh sách Model thành danh sách Dictionary
    data_response = [MedicalDeviceResponse.model_validate(dev).model_dump() for dev in devices]
    
    return format_response(
        status_code=200,
        message="Lấy danh sách thiết bị y tế thành công",
        data=data_response,
        path=request.url.path
    )

# [GET] Lấy thông tin chi tiết một thiết bị y tế
@app.get("/devices/{device_id}", status_code=status.HTTP_200_OK)
def get_device_detail(device_id: int, request: Request, db: Session = Depends(get_db)):
    # Tìm kiếm thiết bị theo ID (Primary Key)
    device = db.query(MedicalDeviceModel).filter(MedicalDeviceModel.id == device_id).first()
    
    if not device:
        # Ngắt tiến trình và ném lỗi 404 (Exception Handler sẽ tự bọc lại thành 6 trường)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
        
    data_response = MedicalDeviceResponse.model_validate(device).model_dump()
    
    return format_response(
        status_code=200,
        message="Lấy chi tiết thiết bị thành công",
        data=data_response,
        path=request.url.path
    )