"""
Giải thích ngắn gọn:

Ứng dụng cung cấp đầy đủ 5 API theo chuẩn RESTful (POST, GET, PUT, DELETE) để quản lý học viên.

API GET /students được tích hợp các Query Parameters (keyword, min_age, max_age) bằng Optional để hỗ trợ lọc danh sách. Điều kiện keyword sẽ kiểm tra chuỗi con (không phân biệt chữ hoa chữ thường) quét qua cả 3 trường: name, code và email.

Sử dụng Pydantic (EmailStr, Field) để tự động kiểm tra tính hợp lệ của dữ liệu đầu vào (ví dụ: định dạng email chuẩn, tuổi lớn hơn 0).

Các API thao tác với ID cụ thể có xử lý bắt lỗi 404 nếu không tìm thấy. API thêm mới (POST) và cập nhật (PUT) được bổ sung logic chặn trùng lặp mã học viên (code) với mã lỗi 400.
"""

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)