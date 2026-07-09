from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum
from datetime import datetime, timezone
import traceback

# ==========================================
# 1. CẤU HÌNH DATABASE & SQLALCHEMY MODEL
# ==========================================
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost/catering_db" # Thay đổi theo cấu hình MySQL của bạn

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dish_code = Column(String(50), unique=True, nullable=False, index=True)
    dish_name = Column(String(100), nullable=False)
    calorie_count = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(30), default="AVAILABLE", nullable=False)

# Tạo bảng (Trong thực tế nên dùng Alembic để migrate)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. PYDANTIC SCHEMAS ĐỂ XÁC THỰC
# ==========================================
class StatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"

class MenuItemBase(BaseModel):
    dish_code: str = Field(..., min_length=1, max_length=50, description="Mã món ăn không được rỗng")
    dish_name: str = Field(..., min_length=1, max_length=100, description="Tên món ăn không được rỗng")
    calorie_count: int = Field(..., gt=0, description="Calo phải lớn hơn 0")
    price: float = Field(..., gt=0, description="Giá phải lớn hơn 0")
    status: StatusEnum = Field(default=StatusEnum.AVAILABLE)

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    # Các trường có thể optional khi PUT/PATCH
    dish_code: Optional[str] = Field(None, min_length=1, max_length=50)
    dish_name: Optional[str] = Field(None, min_length=1, max_length=100)
    calorie_count: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[StatusEnum] = None

class MenuItemResponse(MenuItemBase):
    id: int
    
    # Áp dụng từ model SQLAlchemy
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

# Exception Handler cho Validation (Pydantic) để đảm bảo luôn trả về 6 trường
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return custom_response(
        request=request,
        status_code=400,
        message="Dữ liệu đầu vào không hợp lệ",
        error=str(exc.errors()),
        data=None
    )

# Exception Handler cho lỗi chung (Stack Trace ẩn)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return custom_response(
        request=request,
        status_code=500,
        message="Lỗi hệ thống",
        error="Internal Server Error",
        data=None
    )

# ==========================================
# 4. TRIỂN KHAI 5 API CRUD
# ==========================================

# 1. Thêm món ăn mới (POST)
@app.post("/menu-items")
async def create_menu_item(request: Request, item: MenuItemCreate, db: Session = Depends(get_db)):
    try:
        # Kiểm tra trùng lặp dish_code
        db_item = db.query(MenuItem).filter(MenuItem.dish_code == item.dish_code).first()
        if db_item:
            return custom_response(request, 400, "Mã món ăn đã tồn tại", error="Bad Request")
        
        new_item = MenuItem(**item.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        data_response = MenuItemResponse.model_validate(new_item).model_dump()
        return custom_response(request, 201, "Thêm món ăn thành công", data=data_response)
    except Exception as e:
        db.rollback()
        raise e

# 2. Lấy danh sách toàn bộ món ăn (GET)
@app.get("/menu-items")
async def get_menu_items(request: Request, db: Session = Depends(get_db)):
    items = db.query(MenuItem).all()
    data_response = [MenuItemResponse.model_validate(item).model_dump() for item in items]
    return custom_response(request, 200, "Lấy danh sách thành công", data=data_response)

# 3. Lấy thông tin chi tiết một món ăn (GET)
@app.get("/menu-items/{item_id}")
async def get_menu_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return custom_response(request, 404, "Menu item not found", error="Not Found")
    
    data_response = MenuItemResponse.model_validate(item).model_dump()
    return custom_response(request, 200, "Lấy thông tin món ăn thành công", data=data_response)

# 4. Cập nhật thông tin món ăn (PUT)
@app.put("/menu-items/{item_id}")
async def update_menu_item(request: Request, item_id: int, update_data: MenuItemUpdate, db: Session = Depends(get_db)):
    try:
        item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            return custom_response(request, 404, "Menu item not found", error="Not Found")
        
        # Kiểm tra nếu dish_code bị cập nhật và có bị trùng không
        if update_data.dish_code and update_data.dish_code != item.dish_code:
            existing_code = db.query(MenuItem).filter(MenuItem.dish_code == update_data.dish_code).first()
            if existing_code:
                return custom_response(request, 400, "Mã món ăn cập nhật bị trùng lặp", error="Bad Request")

        # Lọc các trường truyền lên bằng exclude_unset=True
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Ghi đè thuộc tính trực tiếp vào đối tượng SQLAlchemy
        for key, value in update_dict.items():
            setattr(item, key, value)
            
        db.commit()
        db.refresh(item)
        
        data_response = MenuItemResponse.model_validate(item).model_dump()
        return custom_response(request, 200, "Cập nhật món ăn thành công", data=data_response)
    except Exception as e:
        db.rollback()
        raise e

# 5. Xóa món ăn khỏi hệ thống (DELETE)
@app.delete("/menu-items/{item_id}")
async def delete_menu_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            return custom_response(request, 404, "Menu item not found", error="Not Found")
            
        db.delete(item)
        db.commit()
        
        return custom_response(request, 200, "Xóa món ăn thành công", data=None)
    except Exception as e:
        db.rollback()
        raise e