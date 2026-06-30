"""
Phần 1:

Input:

keyword (chuỗi, tùy chọn): Dùng để tìm kiếm một phần tên sản phẩm (không phân biệt hoa/thường).

max_price (số thực, tùy chọn): Dùng để lọc các sản phẩm có giá nhỏ hơn hoặc bằng giá trị này.

Output:

Danh sách các sản phẩm (JSON) thỏa mãn cả 2 điều kiện đầu vào.

Nếu max_price bị âm, trả về thông báo lỗi JSON với key "detail".

Đề xuất giải pháp:

Khai báo 2 tham số trong hàm xử lý logic tương ứng với Query Parameter. Thiết lập giá trị mặc định là None để biến chúng thành tham số không bắt buộc.

Sử dụng điều kiện if để chặn lỗi đầu vào (max_price < 0).

Gán danh sách gốc vào một biến kết quả tạm, sau đó dùng list comprehension để lọc dần qua từng điều kiện.

Các bước xử lý:

Bước 1: Kiểm tra max_price có nhỏ hơn 0 không. Nếu có, trả về ngay thông báo lỗi.

Bước 2: Tạo biến result chứa toàn bộ products.

Bước 3: Nếu có keyword, chuyển cả keyword và name của sản phẩm về chữ thường (thuộc tính .lower()) để lọc không phân biệt hoa thường. Cập nhật lại result.

Bước 4: Nếu có max_price, lọc các sản phẩm có giá <= max_price. Cập nhật lại result.

Bước 5: Trả về biến result.
"""

products = [
    {"id": 1, "name": "Laptop", "price": 15000000},
    {"id": 2, "name": "Mouse", "price": 200000},
    {"id": 3, "name": "Keyboard", "price": 500000},
    {"id": 4, "name": "Monitor", "price": 3000000}
]
from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)