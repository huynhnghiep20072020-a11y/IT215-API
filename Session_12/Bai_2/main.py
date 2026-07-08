from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/shop_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)

class CustomerUpdate(BaseModel):
    full_name: str
    phone: str
    address: str

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id
    ).first()
    
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    customer.full_name = customer_update.full_name
    customer.phone = customer_update.phone
    customer.address = customer_update.address
    
    db.commit()
    db.refresh(customer)
    
    return {
        "message": "Customer updated successfully",
        "data": {
            "id": customer.id,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address
        }
    }

"""
Giải thích ngắn gọn:
1. Thêm `Depends` và `HTTPException` từ `fastapi`, `Session` từ `sqlalchemy.orm`.
2. Hàm `get_db()` sử dụng Dependency Injection với `yield` và `finally db.close()` để quản lý đóng/mở kết nối tự động, chống treo DB.
3. API sử dụng `Depends(get_db)` để gọi session.
4. Xử lý lỗi bằng cách raise `HTTPException` với status code 404 nếu không tìm thấy ID.
5. Gọi `db.commit()` để thực sự lưu dữ liệu thay đổi xuống MySQL và `db.refresh(customer)` để cập nhật trạng thái mới nhất từ DB vào object hiện tại.
"""