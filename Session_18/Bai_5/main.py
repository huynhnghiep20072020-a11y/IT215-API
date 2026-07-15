"""1. Phân tích các lỗi logic trong API cũ (POST /employees)
Lỗi 500 Internal Server Error khi department_id không tồn tại:

Nguyên nhân: Code cũ lấy department = db.query(...).first() nhưng không kiểm tra if department is None: mà gọi trực tiếp department.status ở bên dưới. Điều này gây ra lỗi AttributeError (gọi thuộc tính trên đối tượng None), dẫn đến lỗi 500.

Thêm vượt quá số lượng nhân viên (Vượt max_employees):

Nguyên nhân: Câu lệnh kiểm tra cũ sử dụng if current_count > department.max_employees:. Điều này có nghĩa là nếu phòng ban có tối đa 2 người và hiện tại đang có 2 người, điều kiện 2 > 2 trả về False, hệ thống vẫn cho phép thêm người thứ 3.

Cách sửa: Cần đổi thành dấu >= (lớn hơn hoặc bằng).

Mã nhân viên trùng lặp trên toàn hệ thống:

Nguyên nhân: Code cũ đang truy vấn tìm duplicate_employee bằng cách kết hợp cả employee_code VÀ department_id. Dẫn đến việc nhân viên ở phòng A vẫn có thể dùng mã trùng với nhân viên ở phòng B.

Cách sửa: Xóa điều kiện department_id trong câu truy vấn kiểm tra trùng lặp để đảm bảo tính duy nhất trên toàn CSDL."""


from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship,
    Session
)

DATABASE_URL = "sqlite:///./company.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    max_employees = Column(Integer, nullable=False)

    employees = relationship(
        "Employee",
        back_populates="department"
    )

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    # Khuyến nghị: Nên đặt thêm unique=True ở cấp độ Database để bảo vệ dữ liệu tuyệt đối
    employee_code = Column(String(20), nullable=False, unique=True) 
    full_name = Column(String(100), nullable=False)
    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False
    )

    department = relationship(
        "Department",
        back_populates="employees"
    )

Base.metadata.create_all(bind=engine)

class DepartmentCreate(BaseModel):
    name: str
    status: str
    max_employees: int

class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    department_id: int

class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    full_name: str
    department_id: int
    model_config = ConfigDict(from_attributes=True)

class DepartmentDetailResponse(BaseModel):
    id: int
    name: str
    status: str
    max_employees: int
    employees: List[EmployeeResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

app = FastAPI(
    title="Department Employee API"
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@app.post("/departments")
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db)
):
    department = Department(
        name=data.name,
        status=data.status,
        max_employees=data.max_employees
    )
    db.add(department)
    db.commit()
    db.refresh(department)

    return department

@app.get(
    "/departments/{department_id}",
    response_model=DepartmentDetailResponse
)
def get_department_detail(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Phòng ban không tồn tại"
        )

    return department


# ==========================================
# API ĐÃ ĐƯỢC SỬA VÀ TỐI ƯU
# ==========================================
@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED  # Yêu cầu trả về 201 Created khi thành công
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    # 1. Kiểm tra phòng ban có tồn tại hay không
    department = (
        db.query(Department)
        .filter(Department.id == data.department_id)
        .first()
    )
    
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phòng ban không tồn tại"
        )

    # 2. Kiểm tra trạng thái phòng ban
    if department.status == "INACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phòng ban đã ngừng hoạt động"
        )

    # 3. Kiểm tra số lượng nhân viên hiện tại
    current_count = (
        db.query(Employee)
        .filter(Employee.department_id == data.department_id)
        .count()
    )

    # Sửa lỗi logic: Số lượng hiện tại >= sức chứa tối đa thì không cho thêm
    if current_count >= department.max_employees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phòng ban đã đủ nhân viên"
        )

    # 4. Kiểm tra mã nhân viên trên toàn hệ thống (Bỏ check department_id)
    duplicate_employee = (
        db.query(Employee)
        .filter(Employee.employee_code == data.employee_code)
        .first()
    )

    if duplicate_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã nhân viên đã tồn tại"
        )

    # 5. Khởi tạo và lưu nhân viên mới
    employee = Employee(
        employee_code=data.employee_code,
        full_name=data.full_name,
        department_id=data.department_id
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    return employee