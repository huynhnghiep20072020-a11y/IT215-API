"""
Phần 1: Phân tích lỗi

Gọi GET /products/1 bị lỗi 404 Not Found vì hệ thống chưa định nghĩa đường dẫn động. Nó chỉ đang hiểu một đường dẫn tĩnh duy nhất là "/products/product_id".

Dòng code khai báo sai Path Parameter là: @app.get("/products/product_id")

"/products/product_id" không phải là Path Parameter vì tên biến không được đặt trong cặp dấu ngoặc nhọn {}. Do đó, FastAPI xem chữ "product_id" như một phần của URL cố định.

Endpoint đúng cần sửa thành: @app.get("/products/{product_id}")
"""

products = [
    {"id": 1, "name": "Laptop Dell", "price": 15000000},
    {"id": 2, "name": "Chuột Logitech", "price": 350000},
    {"id": 3, "name": "Bàn phím cơ", "price": 1200000}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)