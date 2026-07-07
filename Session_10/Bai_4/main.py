""""Phần 1: Phân tích Input / OutputInput
(Đầu vào): Tham số shipment_id truyền trực tiếp qua đường dẫn URL (Path Parameter), yêu cầu kiểu dữ liệu là số nguyên (int).
Output thành công (HTTP 200 OK): Trả về một đối tượng JSON chứa thông tin chi tiết của vận đơn khi ID hợp lệ.
Ví dụ: {"id": 123, "tracking_code": "VN-12345", "status": "In Transit"}
Output thất bại (HTTP 404 Not Found): Hệ thống không được crash (sập), chặn đứng Stack Trace và trả về JSON chứa mã lỗi chuẩn RESTful giúp Client dễ dàng xử lý.
Ví dụ: {"detail": "Không tìm thấy mã vận đơn này trong hệ thống."}
Phần 2: So sánh & Lựa chọn giải pháp
Dưới đây là bảng phân tích Trade-off khi bảng shipments phải gánh tải trọng 100.000 bản ghi:
Tiêu chí so sánh
Giải pháp 1: Sử dụng .all() + lọc bằng Python
Giải pháp 2: Sử dụng .first() trực tiếp từ DB
Số lượng bản ghi bị kéo lên bộ nhớ RAM của Server
Kéo toàn bộ 100.000 bản ghi lên RAM cùng một lúc. Gây lãng phí tài nguyên nghiêm trọng, dễ dẫn đến tình trạng vắt kiệt bộ nhớ (Out of Memory) làm sập Server.
Kéo đúng 1 bản ghi duy nhất lên RAM (nếu tìm thấy) hoặc không kéo gì cả (nếu là None). Vô cùng nhẹ nhàng và tiết kiệm tài nguyên.
Câu lệnh SQL sinh ra gửi xuống MySQL
SELECT * FROM shipments;(Tuyệt đối không có lệnh giới hạn nào).
SELECT * FROM shipments WHERE id = ? LIMIT 1;(Chủ động ra lệnh cho MySQL dừng ngay việc tìm kiếm khi thấy kết quả đầu tiên).
Tốc độ xử lý khi dữ liệu phình to (Hiệu năng)
Rất chậm. Ứng dụng phải đợi MySQL truyền 100.000 dòng dữ liệu qua mạng (Network I/O bottleneck). Sau đó, CPU của Python phải chạy vòng lặp độ phức tạp $O(N)$ để tìm ra ID tương ứng.
Cực kỳ nhanh. Tận dụng sức mạnh cốt lõi của Database C Engine. Đặc biệt khi tra cứu bằng cột Khóa chính (id), tốc độ tìm kiếm là $O(1)$ hoặc $O(\log N)$, kết quả trả về chỉ trong vài mili-giây.
Bối cảnh phù hợp để ứng dụng
Chỉ dùng khi thực sự cần tính toán trên toàn bộ dữ liệu: Xuất báo cáo Excel tổng, tính toán thống kê phức tạp mà SQL không hỗ trợ.
Dùng trong 99% các trường hợp tìm kiếm cụ thể: Truy vấn thông tin chi tiết của 1 đối tượng, kiểm tra xem bản ghi có tồn tại hay không (Check exist).
Kết luận lựa chọn:
Đó là lý do tại sao khi review code thực tế, các giảng viên (như thầy Sơn) và các Senior Developer luôn yêu cầu sinh viên/lập trình viên sử dụng 
Giải pháp 2 (.first() hoặc .one_or_none()). Hệ quản trị cơ sở dữ liệu (RDBMS) được sinh ra và tối ưu bằng ngôn ngữ C bậc thấp để làm nhiệm vụ tìm kiếm và lọc dữ liệu cực nhanh. 
Việc ép Python (một ngôn ngữ bậc cao, chạy chậm hơn) tải toàn bộ dữ liệu về rồi mới lọc là hành động chống lại nguyên lý thiết kế hệ thống, gây quá tải RAM (Memory Leak) và nghẽn băng thông mạng."""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# 1. CẤU HÌNH DATABASE MYSQL & SESSION
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. ĐỊNH NGHĨA MODEL CƠ SỞ DỮ LIỆU
# ==========================================
class ShipmentModel(Base):
    __tablename__ = "shipments"
    
    # Cột id là Primary Key (Mặc định đã được đánh Index trong MySQL -> Truy vấn cực nhanh)
    id = Column(Integer, primary_key=True, index=True)
    tracking_code = Column(String(50), unique=True, nullable=False)
    status_info = Column(String(50), nullable=False)

# ==========================================
# 3. SCHEMA ĐẦU RA (PYDANTIC)
# ==========================================
class ShipmentResponse(BaseModel):
    id: int
    tracking_code: str
    status_info: str

    class Config:
        from_attributes = True

app = FastAPI(title="API Quản Lý Kho Vận (Tối ưu Hiệu Năng)")

# ==========================================
# 4. DEPENDENCY QUẢN LÝ VÒNG ĐỜI KẾT NỐI
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Đảm bảo trả lại Connection cho Pool, tránh rò rỉ bộ nhớ

# ==========================================
# 5. API TRA CỨU VẬN ĐƠN (Sử dụng .first())
# ==========================================
@app.get("/shipments/{shipment_id}", response_model=ShipmentResponse, status_code=status.HTTP_200_OK)
def get_shipment_detail(shipment_id: int, db: Session = Depends(get_db)):
    
    # [TỐI ƯU HIỆU NĂNG]
    # Truy vấn đẩy thẳng xuống MySQL với lệnh LIMIT 1 (Thông qua hàm .first())
    # Chỉ kéo 1 bản ghi duy nhất lên RAM của ứng dụng Python, loại bỏ hoàn toàn bẫy dữ liệu 100.000 records.
    shipment = db.query(ShipmentModel).filter(ShipmentModel.id == shipment_id).first()
    
    # [BẢO MẬT HỆ THỐNG]
    # Xử lý chủ động trường hợp MySQL trả về None (Không tìm thấy ID)
    if not shipment:
        # Bắn ra mã lỗi 404 sạch sẽ, chặn đứng Stack Trace thô rò rỉ ra bên ngoài
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy mã vận đơn này trong hệ thống."
        )
        
    return shipment