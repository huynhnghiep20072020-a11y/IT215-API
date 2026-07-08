from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DiscountModel(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=False)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def delete_discount_service(db: Session, discount_id: int):
    discount = db.query(DiscountModel).filter(DiscountModel.id == discount_id).first()
    
    if discount is None:
        raise HTTPException(status_code=404, detail="Mã giảm giá không tồn tại")
        
    if discount.is_active:
        raise HTTPException(status_code=400, detail="Không thể xóa mã giảm giá đang hoạt động")
        
    deleted_data = {
        "id": discount.id,
        "code": discount.code
    }
    
    db.delete(discount)
    db.commit()
    
    return deleted_data

@app.delete("/discounts/{discount_id}")
def delete_discount(discount_id: int, db: Session = Depends(get_db)):
    deleted_discount = delete_discount_service(db, discount_id)
    return {
        "message": "Xóa mã giảm giá thành công",
        "data": deleted_discount
    }

"""
Giải thích ngắn gọn:
1. Hàm get_db() quản lý đóng/mở kết nối MySQL an toàn qua Dependency Injection.
2. Hàm Service delete_discount_service() đảm nhận nghiệp vụ xử lý: tìm bản ghi, kiểm tra tồn tại (báo lỗi 404 nếu None).
3. Tích hợp yêu cầu sáng tạo mở rộng: Kiểm tra trường is_active, chặn việc xóa (báo lỗi 400) nếu mã giảm giá đang hoạt động.
4. Lưu trữ thông tin trước khi xóa, gọi db.delete(discount) để xóa cứng và db.commit() để lưu thay đổi xuống DB.
5. API Router nhận HTTP DELETE, gọi Service và trả về thông tin JSON đúng chuẩn.
"""