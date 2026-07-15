"""BÁO CÁO PHÂN TÍCH VÀ THIẾT KẾ GIẢI PHÁP
6.1. Phân tích dữ liệu đầu vào và đầu ra

Dữ liệu lấy từ Request Body: Cần trích xuất student_id và course_id từ phía Client gửi lên (thông qua API POST /enrollments).

Dữ liệu cần truy vấn từ Database (để kiểm duyệt):

Bản ghi chi tiết của sinh viên (kiểm tra tồn tại và status).

Bản ghi chi tiết của khóa học (kiểm tra tồn tại, status, max_students).

Lịch sử bản ghi Enrollment hiện tại của sinh viên với khóa học (để chống đăng ký trùng).

Tổng số lượng bản ghi Enrollment hiện có của khóa học đó (để so sánh với max_students).

Điều kiện trả về 404 (Not Found):

Mã sinh viên (student_id) không tồn tại trong hệ thống.

Mã khóa học (course_id) không tồn tại trong hệ thống.

Điều kiện trả về 400 (Bad Request):

Sinh viên đang ở trạng thái INACTIVE (không được phép học).

Khóa học đang ở trạng thái CLOSED (ngừng nhận học viên).

Sinh viên đã đăng ký khóa học này trước đó (trùng lặp dữ liệu).

Số lượng học viên hiện tại của khóa học đã đạt hoặc vượt ngưỡng max_students.

Khi nào được phép tạo Enrollment:

Chỉ khi nào request vượt qua toàn bộ 6 lớp kiểm tra nghiệp vụ trên, hệ thống mới khởi tạo đối tượng Enrollment, thêm vào CSDL, commit() và trả về mã 201 Created."""


from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH DATABASE
# ==========================================
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/training_center"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. KHAI BÁO MODELS (ORM)
# ==========================================
class Enrollment(Base):
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    enrolled_at = Column(DateTime, default=func.now())

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    status = Column(String(20), default='ACTIVE')

    enrollments = relationship("Enrollment", back_populates="student")
    courses = relationship("Course", secondary="enrollments", back_populates="students")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    max_students = Column(Integer, nullable=False)
    status = Column(String(20), default='OPEN')

    enrollments = relationship("Enrollment", back_populates="course")
    students = relationship("Student", secondary="enrollments", back_populates="courses")

# ==========================================
# 3. KHAI BÁO SCHEMAS (PYDANTIC)
# ==========================================
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True

class CourseBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StudentCoursesResponse(BaseModel):
    student_id: int = Field(validation_alias="id")
    full_name: str
    courses: List[CourseBasic]

    class Config:
        from_attributes = True
        populate_by_name = True

# ==========================================
# 4. KHAI BÁO FASTAPI & ENDPOINTS
# ==========================================
app = FastAPI()

# Tạo bảng (Trong thực tế nên dùng Alembic)
Base.metadata.create_all(bind=engine)

@app.post("/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def register_course(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    
    # Ktra 1: Sinh viên tồn tại?
    student = db.query(Student).filter(Student.id == enrollment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin sinh viên.")

    # Ktra 2: Khóa học tồn tại?
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin khóa học.")

    # Ktra 3: Trạng thái sinh viên
    if student.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Sinh viên đang ở trạng thái INACTIVE, không thể đăng ký.")

    # Ktra 4: Trạng thái khóa học
    if course.status != "OPEN":
        raise HTTPException(status_code=400, detail="Khóa học đã đóng (CLOSED), ngừng nhận học viên.")

    # Ktra 5: Đăng ký trùng lặp
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.course_id == enrollment.course_id
    ).first()
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký khóa học này trước đó.")

    # Ktra 6: Sức chứa tối đa của khóa học
    current_enrollments_count = db.query(Enrollment).filter(Enrollment.course_id == enrollment.course_id).count()
    if current_enrollments_count >= course.max_students:
        raise HTTPException(status_code=400, detail="Khóa học đã đạt đủ số lượng sinh viên đăng ký tối đa.")

    # 7. Xử lý lưu CSDL khi hợp lệ
    new_enrollment = Enrollment(
        student_id=enrollment.student_id, 
        course_id=enrollment.course_id
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return new_enrollment

@app.get("/students/{student_id}/courses", response_model=StudentCoursesResponse)
def get_student_courses(student_id: int, db: Session = Depends(get_db)):
    
    # Truy vấn thông tin sinh viên
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin sinh viên.")

    # ORM tự động lấy danh sách courses do đã cấu hình parameters secondary
    return student