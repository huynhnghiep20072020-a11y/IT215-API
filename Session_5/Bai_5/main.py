"""

Luồng dữ liệu (Data flow)

Bước 1: Client gửi yêu cầu DELETE kèm theo product_id trên đường dẫn URL (Path Parameter).

Bước 2: Hệ thống tiếp nhận product_id và duyệt danh sách products để tìm kiếm.

Bước 3: Nếu vòng lặp kết thúc mà không có product_id nào khớp, ném ra lỗi HTTP 404 (Product not found).

Bước 4: Nếu tìm thấy sản phẩm, kiểm tra trạng thái is_active. Nếu đã là False, ném ra lỗi HTTP 400 (Product already inactive).

Bước 5: Nếu sản phẩm đang ở trạng thái True, tiến hành gán lại is_active = False (Xóa mềm - Soft Delete).

Bước 6: Trả về thông báo ngừng kinh doanh thành công và dữ liệu sản phẩm vừa được cập nhật.
"""

products = [
    {"id": 1, "code": "SP001", "name": "Keyboard", "price": 500000, "is_active": True},
    {"id": 2, "code": "SP002", "name": "Mouse", "price": 300000, "is_active": True},
    {"id": 3, "code": "SP003", "name": "Monitor", "price": 2500000, "is_active": False}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)