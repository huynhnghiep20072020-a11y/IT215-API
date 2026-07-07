""""STT
Hành vi lỗi trong code hiện tạiHậu quả đối với Database MySQLCách khắc phục bằng SQLAlchemy1
Thiếu lệnh xác thực lưu dữ liệu(Chỉ dùng db.add mà không có db.commit)
Dữ liệu cấu trúc sản phẩm chỉ mới được đưa vào bộ nhớ đệm (Session) của ứng dụng. Do thiếu lệnh commit,
Transaction không bao giờ được hoàn tất để ghi đè xuống ổ cứng của MySQL. Kết quả là bảng dữ liệu trống rỗng.
Thêm lệnh db.commit() ngay sau lệnh db.add(). Có thể dùng thêm db.refresh(new_product) nếu muốn lấy lại ID tự tăng từ database.
2Không giải phóng/đóng Session(Không có db.close())Gây ra tình trạng rò rỉ kết nối (Connection Leak).
Khi Client gửi request liên tục, mỗi request chiếm dụng một kết nối. Rất nhanh chóng, hệ thống sẽ vắt kiệt Connection Pool của database,
gây treo (hang) hoặc sập toàn bộ ứng dụng.Bao bọc logic xử lý trong khối try...finally và gọi db.close() ở finally.
Hoặc chuẩn nhất trong FastAPI là dùng Dependency Injection (Depends) để framework tự động quản lý vòng đời đóng/mở."""


from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float

app = FastAPI()

# Hàm Dependency quản lý tự động đóng/mở Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Đảm bảo luôn đóng kết nối (Giải quyết lỗi số 2)

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        new_product = ProductModel(
            sku=product.sku,
            name=product.name,
            price=product.price
        )
        db.add(new_product)
        
        # Xác thực lưu xuống CSDL (Giải quyết lỗi số 1)
        db.commit()
        db.refresh(new_product)
        
        return {
            "message": "Product created successfully", 
            "data": {"id": new_product.id, "sku": new_product.sku, "name": new_product.name}
        }
    except IntegrityError:
        # Bắt lỗi nếu Client gửi SKU trùng lặp (Bẫy dữ liệu)
        db.rollback() # Rollback transaction để bảo vệ db
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="SKU already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error"
        )
        
""""Những điểm nâng cấp trong code:

status_code=status.HTTP_201_CREATED: Đảm bảo API trả về mã 201 khi tạo mới thành công thay vì mặc định 200.

Depends(get_db): Framework sẽ tự động mở Session khi request đến và chạy db.close()
khi kết thúc request, giải quyết triệt để bài toán Connection Leak.

try...except IntegrityError: Xử lý trường hợp bẫy dữ liệu (Client gửi liên tục các SKU, 
nếu vô tình trùng SKU đã có thì DB sẽ không bị văng lỗi Unhandled Exception mà trả về 400 Bad Request rõ ràng)."""