""""Phần 1: Phân tích Luồng dữ liệu (Data Flow)
Để đảm bảo cấu trúc trả về đồng bộ 6 trường quy chuẩn cho cả hai trạng thái Thành công và Thất bại, 
chúng ta định nghĩa 6 trường đó bao gồm: success (bool), status_code (int), message (str), data (dict | null), error_detail (str | null), và timestamp (str).

Luồng đi của Request được kiểm soát chặt chẽ qua 4 bước:

Tiếp nhận Request: Client gửi customer_id và card_number lên API POST /memberships. FastAPI mở một Session an toàn để kết nối tới MySQL.

Xác thực Khóa Ngoại (Bẫy 1):

Hệ thống gọi lệnh db.query(CustomerModel).filter(...).first() để tìm customer_id trong database.

Nhánh rẽ: Nếu kết quả là None (Khách hàng không tồn tại), hệ thống kích hoạt raise HTTPException(status_code=404).
Khối xử lý ngoại lệ trung tâm sẽ can thiệp, đóng gói lỗi thành JSON 6 trường và trả về Client. Luồng kết thúc ngay lập tức.

Xác thực Dữ liệu Unique (Bẫy 2):

Hệ thống tiếp tục gọi lệnh db.query(MembershipModel).filter(...).first() để xem card_number đã bị ai lấy chưa.

Nhánh rẽ: Nếu tìm thấy bản ghi, hệ thống gọi raise HTTPException(status_code=400). Tương tự, trả về lỗi chuẩn 6 trường. Luồng kết thúc.

Lệnh INSERT an toàn (Thành công):

Chỉ khi vượt qua 2 bẫy trên, hệ thống mới khởi tạo MembershipModel và gọi db.add().

Giao dịch được xác nhận qua db.commit() và db.refresh(). Dữ liệu ghi thành công vào bảng memberships. Trả về mã 201 với cấu trúc JSON 6 trường hoàn chỉnh.

Giải phóng tài nguyên: Khối finally: db.close() dọn dẹp bộ nhớ, trả lại connection cho hệ thống MySQL.

Phần 2: Sản phẩm Mã nguồn Hoàn chỉnh"""


from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime

# ==========================================
# CẤU HÌNH DATABASE
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/crm_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# ĐỊNH NGHĨA MODELS
# ==========================================
class CustomerModel(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

class MembershipModel(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True)
    card_number = Column(String(50), unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))

# ==========================================
# SCHEMA (PYDANTIC) QUẢN LÝ DỮ LIỆU
# ==========================================
class MembershipCreate(BaseModel):
    card_number: str
    customer_id: int

app = FastAPI(title="API Hệ thống CRM VIP")

# ==========================================
# CẤU HÌNH EXCEPTION HANDLER (Đồng bộ 6 trường)
# ==========================================
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Ép buộc tất cả HTTPException (400, 404) phải trả về đúng cấu trúc 6 trường quy chuẩn
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "data": None,
            "error_detail": "Lỗi nghiệp vụ hệ thống",
            "timestamp": datetime.now().isoformat()
        }
    )

# ==========================================
# HÀM DEPENDENCY QUẢN LÝ SESSION
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Luôn giải phóng tài nguyên an toàn

# ==========================================
# API TẠO THẺ THÀNH VIÊN
# ==========================================
@app.post("/memberships", status_code=status.HTTP_201_CREATED)
def create_membership(payload: MembershipCreate, db: Session = Depends(get_db)):
    
    # ----------------------------------------------------
    # BƯỚC 1: XÁC THỰC KHÓA NGOẠI (Customer)
    # ----------------------------------------------------
    customer = db.query(CustomerModel).filter(CustomerModel.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khách hàng không tồn tại trên hệ thống"
        )

    # ----------------------------------------------------
    # BƯỚC 2: XÁC THỰC RÀNG BUỘC DUY NHẤT (Card Number)
    # ----------------------------------------------------
    existing_card = db.query(MembershipModel).filter(MembershipModel.card_number == payload.card_number).first()
    if existing_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã số thẻ thành viên này đã được sử dụng"
        )

    # ----------------------------------------------------
    # BƯỚC 3: TIẾN HÀNH INSERT AN TOÀN
    # ----------------------------------------------------
    new_membership = MembershipModel(
        card_number=payload.card_number,
        customer_id=payload.customer_id
    )
    
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    # ----------------------------------------------------
    # BƯỚC 4: PHẢN HỒI THÀNH CÔNG (Cấu trúc 6 trường)
    # ----------------------------------------------------
    return {
        "success": True,
        "status_code": 201,
        "message": "Tạo thẻ thành viên VIP thành công",
        "data": {
            "id": new_membership.id,
            "card_number": new_membership.card_number,
            "customer_id": new_membership.customer_id
        },
        "error_detail": None,
        "timestamp": datetime.now().isoformat()
    }