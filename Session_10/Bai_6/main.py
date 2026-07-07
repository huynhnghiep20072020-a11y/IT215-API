from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# CẤU HÌNH KẾT NỐI DATABASE
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# ĐỊNH NGHĨA MODEL SQLALCHEMY (Database)
# ==========================================
class ShipmentModel(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="PREPARING")

# Tạo bảng tự động vào MySQL nếu chưa có
Base.metadata.create_all(bind=engine)

# ==========================================
# ĐỊNH NGHĨA SCHEMA PYDANTIC (Data Validation)
# ==========================================
class ShipmentCreate(BaseModel):
    tracking_number: str

class ShipmentResponse(BaseModel):
    id: int
    tracking_number: str
    status: str

    class Config:
        from_attributes = True

app = FastAPI(title="API Quản Lý Vận Đơn")

# ==========================================
# DEPENDENCY QUẢN LÝ SESSION AN TOÀN
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Luôn đóng Session trong khối finally để giải phóng tài nguyên

# ==========================================
# CHỨC NĂNG 1: ĐĂNG KÝ MÃ VẬN ĐƠN MỚI
# ==========================================
@app.post("/shipments", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db)):
    # 1. Truy vấn kiểm tra trùng lặp (Look-before-you-leap)
    existing_shipment = db.query(ShipmentModel).filter(
        ShipmentModel.tracking_number == payload.tracking_number
    ).first()

    # 2. Bắt bẫy dữ liệu: Nếu đã tồn tại thì chặn ngay và ném lỗi 400
    if existing_shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã vận đơn này đã được khởi tạo trước đó"
        )

    # 3. Tạo mới và lưu vĩnh viễn xuống DB
    new_shipment = ShipmentModel(tracking_number=payload.tracking_number)
    db.add(new_shipment)
    db.commit()
    db.refresh(new_shipment) # Lấy lại data (gồm cả ID tự tăng và status default) từ DB
    
    return new_shipment

# ==========================================
# CHỨC NĂNG 2: LẤY DANH SÁCH TẤT CẢ VẬN ĐƠN
# ==========================================
@app.get("/shipments", response_model=list[ShipmentResponse], status_code=status.HTTP_200_OK)
def get_all_shipments(db: Session = Depends(get_db)):
    # Lệnh .all() kéo toàn bộ danh sách bản ghi có trong bảng shipments
    shipments = db.query(ShipmentModel).all()
    
    return shipments


""""Kiểm soát tính hợp lệ của dữ liệu đầu vào: Thay vì nhận chuỗi thô, API dùng Pydantic ShipmentCreate để chắc chắn Client gửi lên đúng JSON có key tracking_number.

Bắt bẫy bảo vệ hệ thống: Lệnh .filter().first() chặn đứng lỗi IntegrityError (trùng khóa Unique) từ cấp ứng dụng trước khi gửi xuống MySQL.

Quản lý Session chặt chẽ: Việc sử dụng Depends(get_db) đảm bảo vòng đời đóng/mở Database kết nối luôn được an toàn qua khối try...finally."""