"""

Input: Danh sách từ điển chứa thông tin sinh viên (có sẵn trong code).

Output: Dữ liệu JSON có cấu trúc gồm "message" (thông báo) và "data" (danh sách sinh viên thỏa mãn điều kiện).

Điều kiện lọc: Thuộc tính "status" của sinh viên phải có giá trị là "active".

Các bước xử lý:

Khởi tạo router/app với method GET và đường dẫn /students/active.

Duyệt qua danh sách sinh viên ban đầu và dùng vòng lặp (hoặc list comprehension) để lọc ra các sinh viên có status == "active".

Kiểm tra nếu mảng kết quả rỗng thì trả về thông báo không có sinh viên.

Ngược lại, trả về danh sách các sinh viên vừa lọc được kèm thông báo thành công.
"""

students = [
    {"id": 1, "name": "An", "status": "active"},
    {"id": 2, "name": "Binh", "status": "inactive"},
    {"id": 3, "name": "Cuong", "status": "active"},
    {"id": 4, "name": "Dung", "status": "pending"}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)