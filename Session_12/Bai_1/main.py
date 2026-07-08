"""
Giải thích ngắn gọn:

Hệ thống được chia nhỏ thành các file độc lập để dễ dàng mở rộng và bảo trì.

Hàm get_db() được tạo để quản lý vòng đời của Database Session bằng cách sử dụng yield kết hợp khối try...finally, đảm bảo kết nối luôn được đóng (db.close()) sau khi hoàn thành request nhằm chống rò rỉ kết nối.

Ở API PUT /products/{product_id}, đối tượng db được tiêm vào qua Depends(get_db). Sau khi gán giá trị mới cho thực thể product, hàm db.commit() được gọi để lưu thay đổi vĩnh viễn xuống MySQL, và db.refresh() để lấy dữ liệu mới nhất từ database trả về cho Client. Trạng thái lỗi 404 được kiểm soát chặt chẽ qua raise HTTPException.
"""

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
from sqlalchemy import Column, Integer, String, Float
from database import Base

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    from pydantic import BaseModel

class ProductUpdate(BaseModel):
    name: str
    price: float
    from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ProductModel
from schemas import ProductUpdate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/products/{product_id}")
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.name = product_update.name
    product.price = product_update.price

    db.commit()
    db.refresh(product)

    return {
        "message": "Product updated successfully",
        "data": {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
    }
    from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)