"""Ràng buộc Pydantic: Ở SmartHomePlanCreate, mình sử dụng Field(..., gt=0) cho hai trường device_quantity và price. Nếu một nhân viên kinh doanh cố tình (hoặc vô tình) nhập số âm (ví dụ: -5 hoặc 0),
Pydantic sẽ tự động hất văng Request ra ngoài với mã lỗi 422 trước khi kịp kết nối với MySQL.

Khối try...except và db.rollback(): Đây là cốt lõi của việc xử lý dữ liệu. Nếu bảng smart_home_plans phát hiện có 1 gói tên "SMART-LITE" đã được insert, 
MySQL sẽ bắn ra lỗi IntegrityError. Hệ thống lập tức nhảy vào except, chạy db.rollback() để tránh kẹt trạng thái giao dịch, sau đó báo lỗi "Plan code already exists" sạch sẽ theo đúng cấu trúc.

Hàm Format Response dùng chung: Việc tách logic cấu trúc 6 trường ra thành hàm format_response giúp các Route code cực kỳ ngắn gọn và dễ bảo trì, mọi Route gọi đến hàm này đều sẽ có khung đồng nhất."""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

# ==========================================
# 1. CẤU HÌNH KẾT NỐI DATABASE MYSQL
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/smarthome_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. ĐỊNH NGHĨA MODEL DATABASE (Bảng smart_home_plans)
# ==========================================
class SmartHomePlanModel(Base):
    __tablename__ = "smart_home_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_code = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(255), nullable=False)
    device_quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False) # Float tương đương với kiểu số thực (Double/Float) trong MySQL

# Tự động tạo bảng nếu database chưa có
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SCHEMA XÁC THỰC INPUT/OUTPUT (PYDANTIC)
# ==========================================
class SmartHomePlanCreate(BaseModel):
    slot_code: str = Field(alias="plan_code", description="Mã gói thiết bị")
    plan_code: str = Field(..., description="Mã gói thiết bị")
    # Ràng buộc không được để rỗng (min_length=1)
    plan_name: str = Field(..., min_length=1, description="Tên gói thiết bị")
    # Ràng buộc phải là số nguyên dương (>0)
    device_quantity: int = Field(..., gt=0, description="Số lượng thiết bị đi kèm")
    # Ràng buộc phải là số thực dương (>0)
    price: float = Field(..., gt=0, description="Đơn giá gói sản phẩm")

class SmartHomePlanResponse(BaseModel):
    id: int
    plan_code: str
    plan_name: str
    device_quantity: int
    price: float

    class Config:
        from_attributes = True

app = FastAPI(title="Hệ Thống Quản Lý Gói Thiết Bị Smart Home")

# ==========================================
# 4. TIỆN ÍCH BỌC DỮ LIỆU & QUẢN LÝ LỖI (6 TRƯỜNG)
# ==========================================
def format_response(status_code: int, message: str, data: dict | list | None, path: str, error: str = None):
    """Hàm chuẩn hóa phản hồi trả về cấu trúc 6 trường"""
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
    """Bắt và bọc các lỗi ngoại lệ thành cấu trúc 6 trường để chặn Stack Trace thô"""
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

# [POST] Thêm mới gói thiết bị
@app.post("/smart-home-plans", status_code=status.HTTP_201_CREATED)
def create_smart_home_plan(
    payload: SmartHomePlanCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    new_plan = SmartHomePlanModel(
        plan_code=payload.plan_code,
        plan_name=payload.plan_name,
        device_quantity=payload.device_quantity,
        price=payload.price
    )
    
    try:
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        
        # Validate data object
        data_response = SmartHomePlanResponse.model_validate(new_plan).model_dump()
        
        return format_response(
            status_code=201,
            message="Thêm gói thiết bị thành công",
            data=data_response,
            path=request.url.path
        )
        
    except IntegrityError:
        # Bắt bẫy dữ liệu: Trùng plan_code (UNIQUE)
        db.rollback() # Hoàn tác để bảo vệ Database
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Plan code already exists"
        )
    except Exception:
        # Bắt các lỗi không xác định khác (bảo vệ Stack Trace)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống khi lưu dữ liệu vào cơ sở dữ liệu"
        )

# [GET] Lấy danh sách toàn bộ gói thiết bị
@app.get("/smart-home-plans", status_code=status.HTTP_200_OK)
def get_all_smart_home_plans(request: Request, db: Session = Depends(get_db)):
    plans = db.query(SmartHomePlanModel).all()
    
    # Serialize list
    data_response = [SmartHomePlanResponse.model_validate(plan).model_dump() for plan in plans]
    
    return format_response(
        status_code=200,
        message="Lấy danh sách thành công",
        data=data_response,
        path=request.url.path
    )

# [GET] Lấy thông tin chi tiết một gói thiết bị theo ID
@app.get("/smart-home-plans/{plan_id}", status_code=status.HTTP_200_OK)
def get_smart_home_plan_detail(plan_id: int, request: Request, db: Session = Depends(get_db)):
    # Tìm kiếm theo ID bằng .first()
    plan = db.query(SmartHomePlanModel).filter(SmartHomePlanModel.id == plan_id).first()
    
    if not plan:
        # Chặn đứng hệ thống khi gọi ID không tồn tại
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
        
    data_response = SmartHomePlanResponse.model_validate(plan).model_dump()
    
    return format_response(
        status_code=200,
        message="Lấy thông tin chi tiết thành công",
        data=data_response,
        path=request.url.path
    )