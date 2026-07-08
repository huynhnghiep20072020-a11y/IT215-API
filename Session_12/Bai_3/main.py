from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/shop_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ShipmentModel(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True)
    tracking_code = Column(String(50), unique=True, nullable=False)
    receiver_name = Column(String(100), nullable=False)
    delivery_address = Column(String(255), nullable=False)

class ShipmentUpdate(BaseModel):
    receiver_name: str
    delivery_address: str

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_shipment_service(db: Session, shipment_id: int, shipment_update: ShipmentUpdate):
    shipment = db.query(ShipmentModel).filter(ShipmentModel.id == shipment_id).first()
    
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    shipment.receiver_name = shipment_update.receiver_name
    shipment.delivery_address = shipment_update.delivery_address
    
    db.commit()
    db.refresh(shipment)
    return shipment

@app.put("/shipments/{shipment_id}")
def update_shipment(shipment_id: int, shipment_update: ShipmentUpdate, db: Session = Depends(get_db)):
    updated_shipment = update_shipment_service(db, shipment_id, shipment_update)
    return {
        "message": "Shipment updated successfully",
        "data": {
            "id": updated_shipment.id,
            "tracking_code": updated_shipment.tracking_code,
            "receiver_name": updated_shipment.receiver_name,
            "delivery_address": updated_shipment.delivery_address
        }
    }

"""
Giải thích ngắn gọn:
1. Hàm `get_db()`: Quản lý vòng đời của database session an toàn, sử dụng `yield` để cung cấp session cho API và đảm bảo đóng kết nối ở khối `finally`.
2. Hàm `update_shipment_service()`: Chịu trách nhiệm logic (Service Layer). Tìm bản ghi bằng `.first()`, raise lỗi 404 nếu rỗng. Tiến hành gán giá trị mới, gọi `db.commit()` để lưu thay đổi vào database và `db.refresh()` để lấy dữ liệu mới nhất.
3. API `@app.put`: Làm nhiệm vụ controller. Nhận tham số URL, body request, và sử dụng `Depends(get_db)` để lấy kết nối database. Sau đó gọi hàm service và trả về kết quả cho client.
"""