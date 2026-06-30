"""
Phần 1: Phân tích & Đề xuất đa giải pháp

Phân tích Input/Output:

Input: Path Parameter product_id (để xác định sản phẩm cần sửa) và Request Body (JSON chứa thông tin code, name, price, stock mới).

Output thành công: Trả về dữ liệu sản phẩm sau khi đã cập nhật thành công (HTTP 200).

Output thất bại: Trả về HTTP 404 nếu sai ID (Product not found), hoặc HTTP 400 nếu trùng mã code (Product code already exists) / sai điều kiện validation (price, stock).

Đề xuất 2 giải pháp:

Giải pháp 1 (Duyệt List): Sử dụng vòng lặp for để quét toàn bộ danh sách products. Khi tìm thấy id khớp thì tiến hành kiểm tra trùng mã code với các phần tử còn lại trước khi cập nhật.

Giải pháp 2 (Dùng Dict): Cấu trúc lại dữ liệu lưu trữ thành dạng Dictionary với key chính là product_id. Khi cần cập nhật, chỉ cần gọi thẳng products[product_id] thay vì phải lặp.

Phần 2: So sánh & Lựa chọn giải pháp

Tốc độ tìm kiếm: List (Chậm, độ phức tạp O(N)) | Dict (Cực nhanh, độ phức tạp O(1)).

Bộ nhớ: List (Tối ưu hơn) | Dict (Tốn thêm một chút bộ nhớ cho cấu trúc băm).

Dễ hiểu: List (Gần gũi với người mới bắt đầu) | Dict (Cần hiểu về key-value map).

Dễ bảo trì: List (Code dài hơn khi tìm kiếm) | Dict (Code ngắn gọn, sạch sẽ).

Bối cảnh phù hợp: List (Dữ liệu rất nhỏ, thay đổi ít) | Dict (Dữ liệu lớn, truy xuất/cập nhật liên tục).

Kết luận lựa chọn: Vì đề bài cung cấp cấu trúc gốc là List các Dictionary, ta chọn Giải pháp 1 kết hợp sức mạnh của thư viện Pydantic để bắt các bẫy dữ liệu tự động, giữ nguyên cấu trúc hệ thống ban đầu.

Phần 3: Triển khai code
"""

products = [
    {"id": 1, "code": "SP001", "name": "Keyboard", "price": 500000, "stock": 10},
    {"id": 2, "code": "SP002", "name": "Mouse", "price": 300000, "stock": 5}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)