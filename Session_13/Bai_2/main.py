from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime, timezone

# ==========================================
# 1. CẤU HÌNH DATABASE & SQLALCHEMY MODEL
# ==========================================
# Cấu hình chuỗi kết nối MySQL (Thay đổi thông tin tương ứng với máy của bạn)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost/pet_boarding_db" 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BoardingSlot(Base):
    __tablename__ = "boarding_slots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_number = Column(String(50), unique=True, nullable=False, index=True)
    room_size = Column(String(30), nullable=False)
    price_per_day = Column(Float, nullable=False)
    status = Column(String(30), default="VACANT", nullable=False)

# Tạo bảng trong database
Base.metadata.create_all(bind=engine)

# Dependency lấy DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. ENUMS & PYDANTIC SCHEMAS ĐỂ XÁC THỰC
# ==========================================
class RoomSizeEnum(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class StatusEnum(str, Enum):
    VACANT = "VACANT"
    OCCUPIED = "OCCUPIED"

class BoardingSlotBase(BaseModel):
    slot_number: str = Field(..., min_length=1, max_length=50, description="Mã khoang chuồng không được để trống")
    room_size: RoomSizeEnum = Field(..., description="Kích thước phòng: SMALL, MEDIUM, LARGE")
    price_per_day: float = Field(..., gt=0, description="Đơn giá mỗi ngày phải lớn hơn 0")
    status: StatusEnum = Field(default=StatusEnum.VACANT, description="Trạng thái: VACANT, OCCUPIED")

class BoardingSlotCreate(BoardingSlotBase):
    pass

class BoardingSlotUpdate(BaseModel):
    slot_number: Optional[str] = Field(None, min_length=1, max_length=50)
    room_size: Optional[RoomSizeEnum] = None
    price_per_day: Optional[float] = Field(None, gt=0)
    status: Optional[StatusEnum] = None

class BoardingSlotResponse(BoardingSlotBase):
    id: int
    
    # Áp dụng from_attributes cho Response mapping từ SQLAlchemy Model
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 3. HELPER: CHUẨN HÓA RESPONSE 6 TRƯỜNG
# ==========================================
def custom_response(request: Request, status_code: int, message: str, data: any = None, error: str = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "statusCode": status_code,
            "message": message,
            "error": error,
            "data": data,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    )

app = FastAPI()

# Exception Handler cho lỗi Validate dữ liệu đầu vào
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return custom_response(
        request=request,
        status_code=400,
        message="Dữ liệu đầu vào không hợp lệ",
        error=str(exc.errors()),
        data=None
    )

# Exception Handler bọc lỗi thô hệ thống (Ngăn rò rỉ Stack Trace)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return custom_response(
        request=request,
        status_code=500,
        message="Đã xảy ra lỗi hệ thống",
        error="Internal Server Error",
        data=None
    )

# ==========================================
# 4. TRIỂN KHAI 5 API CRUD
# ==========================================

# 1. Thêm khoang lưu trú mới (POST)
@app.post("/boarding-slots")
async def create_boarding_slot(request: Request, slot: BoardingSlotCreate, db: Session = Depends(get_db)):
    try:
        # Kiểm tra trùng lặp mã khoang
        existing_slot = db.query(BoardingSlot).filter(BoardingSlot.slot_number == slot.slot_number).first()
        if existing_slot:
            return custom_response(request, 400, "Slot number already exists", error="Bad Request")
        
        new_slot = BoardingSlot(**slot.model_dump())
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)
        
        data_response = BoardingSlotResponse.model_validate(new_slot).model_dump()
        return custom_response(request, 201, "Thêm khoang lưu trú thành công", data=data_response)
    except Exception as e:
        db.rollback() # Hoàn tác giao dịch nếu lỗi
        raise e

# 2. Lấy danh sách tất cả khoang lưu trú (GET)
@app.get("/boarding-slots")
async def get_boarding_slots(request: Request, db: Session = Depends(get_db)):
    slots = db.query(BoardingSlot).all()
    data_response = [BoardingSlotResponse.model_validate(s).model_dump() for s in slots]
    return custom_response(request, 200, "Lấy danh sách thành công", data=data_response)

# 3. Lấy chi tiết thông tin một khoang lưu trú (GET)
@app.get("/boarding-slots/{slot_id}")
async def get_boarding_slot(request: Request, slot_id: int, db: Session = Depends(get_db)):
    slot = db.query(BoardingSlot).filter(BoardingSlot.id == slot_id).first()
    if not slot:
        return custom_response(request, 404, "Boarding slot not found", error="Not Found")
    
    data_response = BoardingSlotResponse.model_validate(slot).model_dump()
    return custom_response(request, 200, "Lấy thông tin chi tiết thành công", data=data_response)

# 4. Cập nhật thông tin khoang lưu trú (PUT)
@app.put("/boarding-slots/{slot_id}")
async def update_boarding_slot(request: Request, slot_id: int, update_data: BoardingSlotUpdate, db: Session = Depends(get_db)):
    try:
        slot = db.query(BoardingSlot).filter(BoardingSlot.id == slot_id).first()
        if not slot:
            return custom_response(request, 404, "Boarding slot not found", error="Not Found")
        
        # Validate logic: Chặn trùng mã slot_number nếu có thay đổi mã
        if update_data.slot_number and update_data.slot_number != slot.slot_number:
            check_exist = db.query(BoardingSlot).filter(BoardingSlot.slot_number == update_data.slot_number).first()
            if check_exist:
                return custom_response(request, 400, "Slot number already exists", error="Bad Request")

        # Bóc tách dữ liệu mới (chỉ lấy các trường được truyền lên)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Ghi đè vào record hiện tại
        for key, value in update_dict.items():
            setattr(slot, key, value)
            
        db.commit()
        db.refresh(slot)
        
        data_response = BoardingSlotResponse.model_validate(slot).model_dump()
        return custom_response(request, 200, "Cập nhật khoang lưu trú thành công", data=data_response)
    except Exception as e:
        db.rollback() # Tránh kẹt phiên DB nếu bị lỗi
        raise e

# 5. Xóa khoang lưu trú khỏi hệ thống (DELETE)
@app.delete("/boarding-slots/{slot_id}")
async def delete_boarding_slot(request: Request, slot_id: int, db: Session = Depends(get_db)):
    try:
        slot = db.query(BoardingSlot).filter(BoardingSlot.id == slot_id).first()
        if not slot:
            return custom_response(request, 404, "Boarding slot not found", error="Not Found")
            
        db.delete(slot)
        db.commit()
        
        return custom_response(request, 200, "Xóa khoang lưu trú thành công", data=None)
    except Exception as e:
        db.rollback()
        raise e