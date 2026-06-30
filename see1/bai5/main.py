"""
Thiết kế kiến trúc routing:

Chủ đề API: Quản lý sản phẩm (Product Management)

Danh sách 8 endpoint (6 cơ bản + 2 mở rộng):

GET /products : Lấy danh sách sản phẩm

GET /products/detail : Xem chi tiết sản phẩm

POST /products : Thêm sản phẩm mới

PUT /products/update : Cập nhật thông tin sản phẩm

DELETE /products/delete : Xóa sản phẩm

GET /products/statistics : Xem thống kê tổng quan về sản phẩm

GET /products/bestsellers : (Mở rộng) Xem danh sách sản phẩm bán chạy nhất

GET /products/out-of-stock : (Mở rộng) Xem danh sách sản phẩm đã hết hàng
"""


from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)