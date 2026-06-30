"""
Phần 1: Phân tích và thiết kế giải pháp

Phân tích bài toán:

Input: Dữ liệu JSON chứa student_id và course_id được gửi qua Request Body.

Output thành công: Trả về HTTP status 201 Created cùng thông tin phiếu đăng ký mới tạo.

Output thất bại: Trả về HTTP status 400 (hoặc 404) kèm thông báo chi tiết (detail) nguyên nhân lỗi (khóa học đầy, đăng ký trùng, hoặc không tồn tại id).

Đề xuất giải pháp:

Sử dụng Pydantic BaseModel để kiểm tra kiểu dữ liệu đầu vào.

Viết logic theo trình tự:

Kiểm tra sự tồn tại của student_id và course_id.

Duyệt mảng registrations để bắt bẫy đăng ký trùng lặp (trùng cả student_id và course_id).

Đếm số lượng bản ghi trong registrations có cùng course_id và so sánh với capacity của courses tương ứng để bắt bẫy khóa học đầy sĩ số.

Nếu vượt qua toàn bộ kiểm tra, tiến hành thêm bản ghi mới và trả về mã 201.
"""

students = [
    {"id": 1, "name": "Nguyen Van A"},
    {"id": 2, "name": "Tran Thi B"},
    {"id": 3, "name": "Le Van C"}
]

courses = [
    {"id": 1, "name": "FastAPI Basic", "capacity": 2},
    {"id": 2, "name": "Python OOP", "capacity": 2}
]

registrations = [
    {"id": 1, "student_id": 1, "course_id": 1},
    {"id": 2, "student_id": 2, "course_id": 1}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)