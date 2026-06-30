"""Phần 1: Chỉ ra lỗi bằng test case cụ thểSTTDữ liệu gửi lên (Request Body)Kết quả hiện tại
(Lỗi)Kết quả đúng mong muốnLỗi phát hiện1{"student_id": "SV001", "course_id": 1}Vẫn tạo được bản ghi đăng ký mới.Báo lỗi học viên đã đăng ký khóa học này (HTTP 400).
Không kiểm tra tổ hợp student_id và course_id đã tồn tại hay chưa.2{"student_id": "SV003", "course_id": 1}Tạo thành công nhưng trả về HTTP status 200 mặc định.Tạo thành công và trả về HTTP status 201 Created.API chưa cấu hình mã trạng thái 201 chuẩn RESTful khi khởi tạo tài nguyên mới.
Phần 2: Sửa lại source codeTách dự án thành các file độc lập.Thêm vòng lặp kiểm tra trùng lặp dựa trên cả student_id và course_id, ném ra HTTPException nếu phát hiện trùng.Bổ sung status_code=status.HTTP_201_CREATED vào decorator của route."""

enrollments = [
    {
        "id": 1,
        "student_id": "SV001",
        "course_id": 1
    },
    {
        "id": 2,
        "student_id": "SV002",
        "course_id": 1
    }
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)