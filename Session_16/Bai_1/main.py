"""Báo cáo lỗi cấu hình
1. Lỗi cấu hình quan hệ 1 - N (Khoa ↔ Sinh viên)

Tên lỗi / Loại quan hệ bị ảnh hưởng: Lỗi khai báo sai tên thuộc tính đồng bộ ngược (back_populates) trong quan hệ 1-N.

Vị trí dòng code gây lỗi: Trong class Department, dòng: students = relationship("Student", back_populates="department_id")

Nguyên nhân gây lỗi: Tham số back_populates của SQLAlchemy yêu cầu phải trỏ đến tên của thuộc tính quan hệ (relationship attribute) ở class đối diện, chứ không phải trỏ vào tên cột Khóa ngoại (Foreign Key). Ở class Student, thuộc tính liên kết là department, nên cấu hình hiện tại khiến SQLAlchemy không thể đồng bộ hai chiều.

Cách khắc phục: Đổi back_populates="department_id" thành back_populates="department".

2. Lỗi cấu hình quan hệ 1 - 1 (Sinh viên ↔ Hồ sơ)

Tên lỗi / Loại quan hệ bị ảnh hưởng: Thiếu cấu hình ép kiểu trả về đối tượng đơn lẻ ở ORM và thiếu ràng buộc duy nhất ở CSDL trong quan hệ 1-1.

Vị trí dòng code gây lỗi:

Trong class Student, dòng: profile = relationship("Profile", back_populates="student")

Trong class Profile, dòng: student_id = Column(Integer, ForeignKey("students.id"))

Nguyên nhân gây lỗi: Về mặt ORM, nếu không khai báo uselist=False, SQLAlchemy sẽ mặc định hiểu đây là quan hệ 1-N và trả về một danh sách (list) các hồ sơ. Về mặt CSDL, nếu khóa ngoại student_id ở bảng Profile không có ràng buộc unique=True, cơ sở dữ liệu vẫn cho phép nhiều hồ sơ trỏ đến cùng một sinh viên.

Cách khắc phục:

Ở class Student, thêm uselist=False thành: profile = relationship("Profile", back_populates="student", uselist=False)

Ở class Profile, thêm unique=True thành: student_id = Column(Integer, ForeignKey("students.id"), unique=True)

3. Lỗi cấu hình quan hệ N - N (Sinh viên ↔ Môn học)

Tên lỗi / Loại quan hệ bị ảnh hưởng: Thiếu tham số liên kết bảng trung gian (secondary) trong quan hệ N-N.

Vị trí dòng code gây lỗi:

Trong class Student, dòng: courses = relationship("Course", back_populates="students")

Trong class Course, dòng: students = relationship("Student", back_populates="courses")

Nguyên nhân gây lỗi: Để thiết lập quan hệ Nhiều - Nhiều, SQLAlchemy bắt buộc phải có tham số secondary trỏ tới bảng trung gian (association table). Nếu không khai báo tham số này, ORM sẽ không biết đường dẫn vật lý để map dữ liệu giữa hai bảng, gây ra lỗi khi truy vấn hoặc thêm dữ liệu.

Cách khắc phục: Bổ sung tham số secondary=student_course vào cả hai hàm relationship ở class Student và class Course.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base 

student_course = Table(
    "student_course", 
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    students = relationship("Student", back_populates="department")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="students")
    
    profile = relationship("Profile", back_populates="student", uselist=False)
    
    courses = relationship("Course", secondary=student_course, back_populates="students")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String(255))
    
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    student = relationship("Student", back_populates="profile")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    
    students = relationship("Student", secondary=student_course, back_populates="courses")