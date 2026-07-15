"""THIẾT KẾ KIẾN TRÚC
7.1. Phân tích nhu cầu

Vấn đề của khách hàng: Việc quản lý thủ công qua Google Form và Excel gây ra sai sót nghiêm trọng về tính toàn vẹn dữ liệu. Cụ thể là không kiểm soát được số lượng đăng ký tối đa, không chặn được các trường hợp đăng ký trùng lặp, đăng ký khi workshop đã đóng cửa, và tốn rất nhiều thời gian để tra cứu chéo danh sách sinh viên theo workshop hoặc ngược lại.

Người dùng chính của hệ thống:

Nhân viên quản lý trung tâm (Tạo workshop, duyệt danh sách, quản lý trạng thái).

Sinh viên (Thực hiện đăng ký, xem lịch sử workshop đã đăng ký).

Hệ thống cần giải quyết các chức năng: Quản lý thông tin hai thực thể chính (Student, Workshop) và tự động hóa khâu kiểm duyệt nghiệp vụ đăng ký (Registration) nhằm chặn đứng mọi dữ liệu không hợp lệ ngay từ đầu vào API.

Chức năng quan trọng nhất: Endpoint POST /registrations. Đây là "trái tim" của hệ thống, nơi phải gánh toàn bộ logic kiểm tra chéo (capacity, duplicates, states, datetime) để đảm bảo tính toàn vẹn của dữ liệu.

Các quyết định thiết kế nghiệp vụ:

Trạng thái Workshop: OPEN (Đang nhận đăng ký), CLOSED (Đã chốt danh sách), CANCELLED (Bị hủy).

Trạng thái Student: ACTIVE (Đang hoạt động, được phép đăng ký), INACTIVE (Đình chỉ/Đã ra trường, không được đăng ký).

Hủy đăng ký: Áp dụng Soft-delete (cập nhật trạng thái bảng Registration thành CANCELLED) thay vì xóa vật lý (Hard-delete) để giữ lại lịch sử tương tác của sinh viên.

Sinh viên Inactive: Chặn ở cấp API, không cho phép tạo Registration mới.

Thời gian Workshop: Chặn đăng ký nếu start_time <= thời gian hiện tại của hệ thống.

Ràng buộc duy nhất: Cả student_code và email đều phải unique=True.

Định dạng dữ liệu trả về: API trả về dữ liệu lồng nhau (Nested JSON) khi truy xuất quan hệ (ví dụ: lấy chi tiết Student sẽ kèm theo list các object Workshop liên kết) thông qua cấu hình orm_mode.

Kiến trúc: Tách bạch Router (tiếp nhận HTTP) và Services (xử lý logic nghiệp vụ) để code dễ bảo trì.

7.2. Thiết kế cơ sở dữ liệu

Bảng students:

Khóa chính: id (Integer)

Ràng buộc: student_code và email là Unique.

Bảng workshops:

Khóa chính: id (Integer)

Bảng registrations (Bảng trung gian N-N):

Khóa chính: id (Integer)

Khóa ngoại 1: student_id trỏ về students.id

Khóa ngoại 2: workshop_id trỏ về workshops.id

Quan hệ: Student 1 - N Registration N - 1 Workshop."""


from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import engine, Base, get_db
import schemas
import services

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workshop Registration API")

@app.post("/students", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return services.create_student(db, student)

@app.get("/students", response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return services.get_students(db)

@app.post("/workshops", response_model=schemas.WorkshopResponse, status_code=status.HTTP_201_CREATED)
def create_workshop(workshop: schemas.WorkshopCreate, db: Session = Depends(get_db)):
    return services.create_workshop(db, workshop)

@app.get("/workshops", response_model=List[schemas.WorkshopResponse])
def get_workshops(db: Session = Depends(get_db)):
    return services.get_workshops(db)

@app.get("/workshops/{id}", response_model=schemas.WorkshopResponse)
def get_workshop(id: int, db: Session = Depends(get_db)):
    return services.get_workshop_by_id(db, id)

@app.post("/registrations", response_model=schemas.RegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_registration(registration: schemas.RegistrationCreate, db: Session = Depends(get_db)):
    return services.register_workshop(db, registration)

@app.get("/students/{id}/workshops", response_model=schemas.StudentWithWorkshopsResponse)
def get_student_workshops(id: int, db: Session = Depends(get_db)):
    return services.get_student_workshops(db, id)

@app.get("/workshops/{id}/students", response_model=schemas.WorkshopWithStudentsResponse)
def get_workshop_students(id: int, db: Session = Depends(get_db)):
    return services.get_workshop_students(db, id)

@app.put("/registrations/{id}", response_model=schemas.RegistrationResponse)
def cancel_registration(id: int, db: Session = Depends(get_db)):
    return services.cancel_registration(db, id)