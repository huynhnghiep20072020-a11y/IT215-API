"""
Phần 1: Phân tích lỗi

Endpoint hiện tại có sử dụng Path Parameter.

Path Parameter trong bài này là {status}.

Khi gọi GET /orders/status/pending, biến status nhận giá trị là chuỗi "pending".

API hiện tại trả về sai dữ liệu vì hàm xử lý không sử dụng biến status để lọc danh sách mà trả về toàn bộ dữ liệu gốc.

Dòng code đang khiến API bỏ qua giá trị status là: return orders.
"""

orders = [
    {"id": 1, "customer_name": "Nguyễn Văn An", "total": 250000, "status": "pending"},
    {"id": 2, "customer_name": "Trần Thị Bình", "total": 500000, "status": "paid"},
    {"id": 3, "customer_name": "Lê Văn Cường", "total": 150000, "status": "cancelled"},
    {"id": 4, "customer_name": "Phạm Thị Dung", "total": 320000, "status": "pending"}
]
from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)