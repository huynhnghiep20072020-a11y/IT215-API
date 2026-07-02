"""
Phần 1: Báo cáo phân tích và thiết kế giải pháp

Phân tích bài toán (I/O):

Input Schema: JSON Body chứa product_id (int) và quantity (int).

Output thành công: API trả về HTTP Status 201 Created cùng với thông tin đơn hàng vừa tạo.

Output thất bại: Trả về HTTP Status 400 Bad Request kèm theo thông báo lỗi chi tiết theo bẫy dữ liệu, 
hoặc 404 Not Found nếu ID sản phẩm không tồn tại.

Thiết kế các bước xử lý (Logic Flow):

Bước 1: Tiếp nhận request, kiểm tra ngay điều kiện quantity <= 0. Nếu đúng, chặn lại và ném lỗi 400.

Bước 2: Tìm kiếm sản phẩm trong products_db dựa trên product_id. Nếu không tìm thấy, ném lỗi 404.

Bước 3: So sánh quantity với thuộc tính stock của sản phẩm. Nếu quantity > stock, ném lỗi 400.

Bước 4: Nếu qua hết các bẫy trên, tiến hành cập nhật giảm số lượng trong kho (stock -= quantity).

Bước 5: Khởi tạo bản ghi đơn hàng mới, thêm vào danh sách orders_db và trả về mã thành công 201.
"""

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)