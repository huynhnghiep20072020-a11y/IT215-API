""""Pydantic Validations: Ở lớp ParkingSlotCreate, các hàm Field(..., min_length=3) và Field(..., gt=0) đảm nhận việc chặn ngay lập tức các yêu cầu nhập vùng trống hoặc số âm.
Client sẽ bị từ chối với lỗi 422 trước khi kịp chạm tới cơ sở dữ liệu.

Safety Transaction (db.rollback()): Thay vì check .filter().first() như cách thủ công, API POST tận dụng chức năng bắt lỗi IntegrityError của SQLAlchemy khi MySQL từ chối dữ liệu trùng lặp slot_code.
Ngay lập tức, lệnh db.rollback() được thực thi để hủy bỏ giao dịch, đảm bảo MySQL không bị treo nghẽn.

Centralized Exception Handling (@app.exception_handler): Kỹ thuật này giúp bạn không phải viết thủ công JSON trả về trong mỗi câu lệnh raise HTTPException. 
Bạn cứ ném lỗi bình thường, hệ thống tự động tóm lấy và đúc thành khuôn 6 trường như thiết kế. Điều này giúp mã nguồn vô cùng sạch sẽ và dễ bảo trì.
Dữ liệu Request URL cũng được lấy tự động qua biến request.url.path."""



from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

# ==========================================
# 1. CẤU HÌNH DATABASE
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/parking_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. ĐỊNH NGHĨA MODEL DATABASE
# ==========================================
class ParkingSlotModel(Base):
    __tablename__ = "parking_slots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    slot_code = Column(String(50), unique=True, nullable=False)
    zone_name = Column(String(255), nullable=False)
    max_weight = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

# Tự động tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SCHEMA XÁC THỰC DỮ LIỆU (PYDANTIC)
# ==========================================
class ParkingSlotCreate(BaseModel):
    slot_code: str = Field(..., description="Mã vị trí đỗ xe")
    # Ràng buộc zone_name tối thiểu 3 ký tự
    zone_name: str = Field(..., min_length=3, description="Tên khu vực đỗ xe")
    # Ràng buộc max_weight phải lớn hơn 0
    max_weight: int = Field(..., gt=0, description="Tải trọng tối đa")

class ParkingSlotResponse(BaseModel):
    id: int
    slot_code: str
    zone_name: str
    max_weight: int
    is_available: bool

    class Config:
        from_attributes = True

app = FastAPI(title="Hệ Thống Quản Lý Bãi Đỗ Xe")

# ==========================================
# 4. TIỆN ÍCH: FORMAT RESPONSE 6 TRƯỜNG & MIDDLEWARE LỖI
# ==========================================
def format_response(status_code: int, message: str, data: dict, path: str, error: str = None):
    """Hàm hỗ trợ bọc dữ liệu trả về theo đúng cấu trúc 6 trường quy chuẩn"""
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        # Trả về chuỗi ISO format có chữ 'Z' ở cuối biểu thị UTC
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Bắt mọi ngoại lệ HTTPException và format lại thành cấu trúc 6 trường"""
    # Xác định chuỗi Error dựa trên status_code
    error_str = "Not Found" if exc.status_code == 404 else "Bad Request" if exc.status_code == 400 else "Error"
    
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

# Hàm Dependency quản lý session an toàn
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 5. CÁC API NGHIỆP VỤ
# ==========================================

# [POST] Thêm vị trí đỗ xe mới
@app.post("/parking-slots", status_code=status.HTTP_201_CREATED)
def create_parking_slot(
    payload: ParkingSlotCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    # Khởi tạo đối tượng model từ dữ liệu hợp lệ
    new_slot = ParkingSlotModel(
        slot_code=payload.slot_code,
        zone_name=payload.zone_name,
        max_weight=payload.max_weight
    )
    
    # Bọc giao dịch trong khối try-except để chống crash và tự động Rollback
    try:
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)
        
        # Parse Pydantic model sang Dictionary để cho vào "data"
        data_response = ParkingSlotResponse.model_validate(new_slot).model_dump()
        
        return format_response(
            status_code=201,
            message="Thêm vị trí đỗ xe thành công",
            data=data_response,
            path=request.url.path
        )
        
    except IntegrityError:
        # Xảy ra khi insert trùng slot_code (vi phạm ràng buộc UNIQUE của MySQL)
        db.rollback() # Bắt buộc ROLLBACK để giải phóng tiến trình
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Mã vị trí đỗ đã tồn tại trên hệ thống"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống khi lưu dữ liệu"
        )

# [GET] Lấy danh sách toàn bộ vị trí đỗ xe
@app.get("/parking-slots", status_code=status.HTTP_200_OK)
def get_all_parking_slots(request: Request, db: Session = Depends(get_db)):
    slots = db.query(ParkingSlotModel).all()
    
    # Chuyển đổi danh sách Model Objects sang danh sách Dictionary
    data_response = [ParkingSlotResponse.model_validate(slot).model_dump() for slot in slots]
    
    return format_response(
        status_code=200,
        message="Lấy danh sách vị trí đỗ xe thành công",
        data=data_response,
        path=request.url.path
    )

# [GET] Lấy thông tin chi tiết một vị trí đỗ xe
@app.get("/parking-slots/{slot_id}", status_code=status.HTTP_200_OK)
def get_parking_slot_detail(slot_id: int, request: Request, db: Session = Depends(get_db)):
    # Tìm kiếm theo Primary Key
    slot = db.query(ParkingSlotModel).filter(ParkingSlotModel.id == slot_id).first()
    
    # Nếu không tìm thấy, ném lỗi 404 (Exception Handler sẽ tự bọc lại thành 6 trường)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking slot not found"
        )
        
    data_response = ParkingSlotResponse.model_validate(slot).model_dump()
    
    return format_response(
        status_code=200,
        message="Lấy chi tiết vị trí đỗ xe thành công",
        data=data_response,
        path=request.url.path
    )