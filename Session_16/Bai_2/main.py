"""Báo cáo lỗi cấu hình
1. Lỗi cấu hình quan hệ 1 - N (Phòng ban ↔ Nhân viên)

Tên lỗi / Loại quan hệ bị ảnh hưởng: Lỗi khai báo sai tên thuộc tính đồng bộ ngược trong quan hệ 1-N.

Vị trí dòng code gây lỗi: Trong class Department, dòng: employees = relationship("Employee", back_populates="department_id")

Nguyên nhân gây lỗi: Tham số back_populates yêu cầu khai báo tên của thuộc tính relationship tương ứng ở class đối diện, không phải là tên cột Khóa ngoại (Foreign Key). Ở class Employee, thuộc tính liên kết được đặt tên là department, do đó việc trỏ vào department_id khiến SQLAlchemy không thể thiết lập liên kết hai chiều.

Cách khắc phục: Sửa back_populates="department_id" thành back_populates="department".

2. Lỗi cấu hình quan hệ 1 - 1 (Nhân viên ↔ Thiết bị)

Tên lỗi / Loại quan hệ bị ảnh hưởng: Thiếu cấu hình ép kiểu trả về đối tượng đơn lẻ ở ORM và thiếu ràng buộc duy nhất ở CSDL trong quan hệ 1-1.

Vị trí dòng code gây lỗi:

Trong class Employee, dòng: device = relationship("Device", back_populates="employee")

Trong class Device, dòng: employee_id = Column(Integer, ForeignKey("employees.id"))

Nguyên nhân gây lỗi: Nếu không có tham số uselist=False, SQLAlchemy mặc định hiểu đây là quan hệ 1-N và sẽ trả về một mảng (danh sách) các thiết bị. Đồng thời, dưới cơ sở dữ liệu, nếu cột employee_id ở bảng devices không có ràng buộc unique=True, hệ thống vẫn sẽ cho phép chèn nhiều bản ghi thiết bị cùng trỏ về một nhân viên.

Cách khắc phục:

Tại class Employee, bổ sung uselist=False: device = relationship("Device", back_populates="employee", uselist=False)

Tại class Device, bổ sung unique=True: employee_id = Column(Integer, ForeignKey("employees.id"), unique=True)

3. Lỗi cấu hình quan hệ N - N (Nhân viên ↔ Dự án)

Tên lỗi / Loại quan hệ bị ảnh hưởng: Thiếu cấu hình liên kết bảng trung gian trong quan hệ N-N.

Vị trí dòng code gây lỗi:

Trong class Employee, dòng: projects = relationship("Project", back_populates="employees")

Trong class Project, dòng: employees = relationship("Employee", back_populates="projects")

Nguyên nhân gây lỗi: Trong quan hệ Nhiều - Nhiều, ORM cần biết bảng vật lý nào đang làm cầu nối lưu trữ các cặp khóa ngoại. Việc thiếu tham số secondary khiến SQLAlchemy không tìm được đường dẫn ánh xạ qua bảng trung gian employee_project, dẫn đến lỗi khi truy vấn hoặc thêm dữ liệu.

Cách khắc phục: Thêm tham số secondary=employee_project vào trong hàm relationship() ở cả class Employee và class Project."""


from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

employee_project = Table(
    "employee_project",
    Base.metadata,
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True)
)

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="employees")
    
    device = relationship("Device", back_populates="employee", uselist=False)
    
    projects = relationship("Project", secondary=employee_project, back_populates="employees")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(50), unique=True, nullable=False)
    
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True)
    employee = relationship("Employee", back_populates="device")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    
    employees = relationship("Employee", secondary=employee_project, back_populates="projects")