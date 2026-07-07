""""Bảng phân tích Test Case lỗi
STT
Phương thức truy vấn hiện tạiTình huống gây lỗi (Edge Case)Phương thức thay thế an toàn hơn1.
one()Truy vấn một ID không tồn tại (VD: order_id = 999). Hàm .one() ép buộc phải có chính xác 1 bản ghi được trả về.
Nếu không có (0 bản ghi), nó sẽ lập tức văng ra lỗi hệ thống NoResultFound, khiến FastAPI không kịp xử lý và trả về lỗi 500 kèm Stack Trace.
Đổi sang dùng .first(). Hàm này sẽ lấy bản ghi đầu tiên, nếu không tìm thấy sẽ nhẹ nhàng trả về giá trị None mà không gây crash.
Sau đó ta chủ động dùng lệnh if not để ném ra lỗi 404 Not Found."""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# CẤU HÌNH DATABASE
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100))
    total_price = Column(Integer)

app = FastAPI()

# ==========================================
# HÀM QUẢN LÝ SESSION (Chống tràn bộ nhớ)
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Luôn đóng kết nối sau khi request kết thúc

# ==========================================
# API LẤY THÔNG TIN ĐƠN HÀNG (Đã fix lỗi)
# ==========================================
@app.get("/orders/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    
    # -----------------------------------------------------------------
    # BƯỚC 1: TRUY VẤN DỮ LIỆU BẰNG .first() THAY VÌ .one()
    # - Nếu có order_id = 1 -> order chứa object OrderModel.
    # - Nếu order_id = 999 (không tồn tại) -> order nhận giá trị None (không bị crash).
    # -----------------------------------------------------------------
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    # -----------------------------------------------------------------
    # BƯỚC 2: XỬ LÝ LỖI BẢO MẬT (Chặn Stack Trace)
    # Kiểm tra xem biến order có phải là None hay không.
    # Nếu là None, chủ động ném ra HTTP 404 với thông báo ẩn danh, 
    # không tiết lộ cấu trúc DB ra bên ngoài.
    # -----------------------------------------------------------------
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found" # Chỉ hiện dòng này cho Client
        )
        
    # -----------------------------------------------------------------
    # BƯỚC 3: TRẢ VỀ KẾT QUẢ THÀNH CÔNG
    # Nếu code chạy đến đây nghĩa là tìm thấy đơn hàng.
    # -----------------------------------------------------------------
    return {
        "id": order.id, 
        "customer": order.customer_name,
        "total_price": order.total_price
    }