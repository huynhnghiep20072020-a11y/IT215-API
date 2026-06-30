"""
Endpoint hiện tại trong source code cũ là: /student

Gọi GET /students bị lỗi 404 Not Found vì route này chưa được khai báo trong code, hệ thống chỉ đang có route /student.

Tên endpoint /student chưa phù hợp vì khi lấy danh sách nhiều đối tượng, chuẩn RESTful API yêu cầu sử dụng danh từ số nhiều.

Dòng return students[0] sai nghiệp vụ vì nó chỉ lấy phần tử đầu tiên trong mảng thay vì trả về toàn bộ mảng dữ liệu.

Đường dẫn API đúng theo yêu cầu khách hàng là: /students
"""



students = [
    {"id": 1, "name": "Nguyen Van A", "age": 20},
    {"id": 2, "name": "Tran Thi B", "age": 21},
    {"id": 3, "name": "Le Van C", "age": 20}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)
