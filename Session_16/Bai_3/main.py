"""Báo cáo thiết kế giải pháp mô hình hóa (Database Design)
Sơ đồ quan hệ thực thể (ERD)
Mối quan hệ Nhiều - Nhiều (N-N) giữa Sinh viên và Khóa học không thể kết nối trực tiếp trong cơ sở dữ liệu quan hệ mà phải được phân rã thành hai mối quan hệ 1-N thông qua một bảng trung gian:

Student (1) - (N) Enrollment (N) - (1) Course

Thực thể Student có quan hệ 1-N với Enrollment.

Thực thể Course có quan hệ 1-N với Enrollment.

Xác định vị trí đặt Khóa ngoại (Foreign Key)

Bảng con (Child Table): Enrollment (Bảng trung gian).

Lý do: Khóa ngoại luôn được đặt ở bảng mang ý nghĩa "Nhiều" (N) trong mối quan hệ 1-N nhằm đảm bảo tính toàn vẹn tham chiếu. Một bản ghi đăng ký (Enrollment) bắt buộc phải thuộc về một sinh viên cụ thể (student_id) và một khóa học cụ thể (course_id). Việc đặt khóa ngoại tại đây giúp cơ sở dữ liệu chặn đứng các dữ liệu rác (ví dụ: đăng ký một khóa học không tồn tại).

Cơ chế đồng bộ của ORM (back_populates)

Tham số back_populates trong SQLAlchemy đóng vai trò khai báo sự liên kết hai chiều cho các thuộc tính ảo của mô hình ở tầng ứng dụng (ORM).

Khi có sự thay đổi ở một đầu của mối quan hệ (ví dụ: gán một đối tượng Course vào danh sách student.courses), SQLAlchemy sẽ sử dụng back_populates để tự động cập nhật danh sách ở đầu bên kia (course.students) ngay trong phiên làm việc (session) bộ nhớ trước khi lưu xuống cơ sở dữ liệu. Điều này cho phép lập trình viên truy vấn chéo dữ liệu một cách đồng bộ mà không cần tải lại trang thái từ database."""


from fastapi import FastAPI
from schemas import EnrollmentCreate, EnrollmentResponse, StudentCoursesResponse

app = FastAPI()

@app.post("/enrollments", response_model=EnrollmentResponse, status_code=201)
def create_enrollment(enrollment: EnrollmentCreate):
    pass

@app.get("/students/{student_id}/courses", response_model=StudentCoursesResponse)
def get_student_courses(student_id: int):
    pass