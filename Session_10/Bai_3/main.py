""""Phần 1: Báo cáo phân tích bài toán
1. Phân tích Input / Output

Dữ liệu đầu vào (Input): Client chỉ được phép gửi lên 2 trường thông tin cần thiết nhất để tạo kho mới. Bỏ qua trường id vì cơ sở dữ liệu sẽ tự động sinh ra.

warehouse_code: Kiểu chuỗi (String).

location: Kiểu chuỗi (String).

Dữ liệu đầu ra (Output):

Trường hợp thành công: Trả về HTTP Status 201 Created kèm theo toàn bộ thông tin kho vừa tạo (Bao gồm cả id vừa được cấp).

Trường hợp thất bại (Trùng mã kho): Trả về HTTP Status 400 Bad Request kèm theo thông báo lỗi quy chuẩn, ngăn chặn việc hiển thị Stack Trace ra ngoài.

2. Thiết kế các bước tuần tự (Thuật toán xử lý)
Thuật toán được triển khai tuần tự theo các bước bảo vệ sau:

Mở kết nối: Nhận request và tự động mở một phiên làm việc (Session) với cơ sở dữ liệu MySQL thông qua Dependency Injection.

Truy vấn (SELECT trước): Dùng lệnh db.query(InventoryModel).filter(InventoryModel.warehouse_code == input.warehouse_code).first().

Kiểm tra điều kiện:

Nếu kết quả trả về có dữ liệu (Khác None): Ngay lập tức dùng raise HTTPException để ném ra lỗi 400 kèm câu thông báo "Mã kho vận đã tồn tại trên hệ thống, không thể tạo trùng", luồng xử lý bị chặn đứng tại đây.

Nếu kết quả trả về không có dữ liệu (None): Cho phép đi tiếp xuống bước 4.

Ghi dữ liệu (INSERT): Khởi tạo đối tượng InventoryModel bằng dữ liệu đầu vào.

Xác thực: Gọi db.add() để đưa vào hàng đợi và db.commit() để chốt giao dịch xuống ổ cứng của MySQL.

Đóng kết nối: Giải phóng Session để trả lại tài nguyên cho Connection Pool."""


from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# 1. CẤU HÌNH KẾT NỐI MYSQL
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. ĐỊNH NGHĨA MODEL DATABASE (SQLAlchemy)
# ==========================================
class InventoryModel(Base):
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True, index=True)
    warehouse_code = Column(String(50), unique=True, nullable=False)
    location = Column(String(100), nullable=False)

# Tự động tạo bảng nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. ĐỊNH NGHĨA SCHEMA KIỂM SOÁT INPUT/OUTPUT (Pydantic)
# ==========================================
class InventoryCreate(BaseModel):
    warehouse_code: str
    location: str

class InventoryResponse(BaseModel):
    id: int
    warehouse_code: str
    location: str

    class Config:
        from_attributes = True

app = FastAPI(title="Hệ thống Quản lý Kho Vận")

# ==========================================
# 4. HÀM QUẢN LÝ VÒNG ĐỜI SESSION (An toàn)
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Luôn đóng phiên sau khi trả response

# ==========================================
# 5. API ĐĂNG KÝ KHO VẬN (Xử lý nghiệp vụ chọn lọc)
# ==========================================
@app.post("/inventories", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(inventory_data: InventoryCreate, db: Session = Depends(get_db)):
    # BƯỚC 1: Chủ động SELECT kiểm tra thực trạng trước
    # Lấy ra kho hàng đầu tiên có mã warehouse_code giống với mã Client gửi lên
    existing_inventory = db.query(InventoryModel).filter(
        InventoryModel.warehouse_code == inventory_data.warehouse_code
    ).first()

    # BƯỚC 2: Bắt bẫy dữ liệu (Ngăn chặn IntegrityError / Duplicate Entry)
    if existing_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã kho vận đã tồn tại trên hệ thống, không thể tạo trùng"
        )

    # BƯỚC 3: Nếu không trùng, tiến hành INSERT dữ liệu mới
    new_inventory = InventoryModel(
        warehouse_code=inventory_data.warehouse_code,
        location=inventory_data.location
    )
    db.add(new_inventory)
    db.commit() # Xác thực giao dịch lưu xuống CSDL
    db.refresh(new_inventory) # Làm mới để lấy ID tự tăng do DB cấp

    return new_inventory