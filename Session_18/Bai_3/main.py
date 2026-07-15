"""PHẦN 1: PHÂN TÍCH VÀ ĐỀ XUẤT ĐA GIẢI PHÁP
6.1. Phân tích đầu vào và đầu raDữ liệu phải được kiểm tra đầu tiên: Kiểm tra sự tồn tại của Khóa học (Course) thông qua tham số course_id.
Nếu khóa học không tồn tại trong CSDL, hệ thống phải dừng lại và ném ra ngoại lệ HTTP 404 Not Found ngay lập tức.Điều kiện dùng để lọc Enrollment:
Thuộc tính status của bảng Enrollment phải nằm trong tập hợp ["STUDYING", "COMPLETED"]. Bỏ qua các bản ghi có trạng thái CANCELLED hoặc bất kỳ trạng thái nào khác.Điều kiện dùng để lọc Student:
Thuộc tính status của bảng Student phải mang giá trị chính xác là "ACTIVE".Cách loại bỏ sinh viên trùng: Một sinh viên có thể đăng ký, hủy, rồi đăng ký lại cùng một khóa học, dẫn đến nhiều bản ghi Enrollment
Để loại trùng, cần áp dụng từ khóa DISTINCT trong câu lệnh SQL hoặc ORM query, đảm bảo mỗi đối tượng Student chỉ xuất hiện một lần trong kết quả.Trường hợp trả về danh sách rỗng: Trả về khi Khóa học tồn tại hợp lệ,
nhưng không có bất kỳ bản ghi Enrollment nào thỏa mãn điều kiện trạng thái, hoặc tất cả sinh viên đăng ký đều đang ở trạng thái "INACTIVE".6.2. Đề xuất tối thiểu hai giải phápGiải pháp 1: 
Truy vấn Enrollment rồi dùng vòng lặp (App-level filtering)Truy vấn thông tin Course. Sau đó, truy vấn toàn bộ danh sách Enrollment của khóa học này. Dùng vòng lặp for duyệt qua từng Enrollment,
kiểm tra trạng thái đăng ký. Nếu thỏa mãn, tiếp tục kiểm tra trạng thái của Student liên kết. Đưa các sinh viên hợp lệ vào một cấu trúc dữ liệu Set (để loại trùng), chuyển về List,
tự viết hàm sort() sắp xếp theo tên bằng Python và trả về.Giải pháp 2: Sử dụng JOIN giữa Student và Enrollment (Database-level filtering)Khởi tạo một câu truy vấn xuất phát từ bảng Student, thực hiện JOIN với bảng Enrollment.
Gắn trực tiếp toàn bộ các điều kiện lọc (Mã khóa học, Trạng thái đăng ký, Trạng thái sinh viên) vào mệnh đề WHERE (filter trong ORM). Áp dụng hàm distinct() và order_by() ngay trên câu truy vấn SQL để CSDL xử lý việc loại trùng và sắp xếp.
PHẦN 2: SO SÁNH VÀ LỰA CHỌN6.3. Lập bảng so sánhTiêu chíGiải pháp dùng vòng lặpGiải pháp dùng JOINĐộ dễ hiểuTrực quan, dễ viết logic đối với người mới bắt đầu.Yêu cầu kiến thức vững về SQL và ánh xạ ORM.
Số câu truy vấnGây lỗi N+1 Query (1 truy vấn lấy Enrollment, N truy vấn lấy Student).Tối ưu với 1 đến 2 câu truy vấn duy nhất.Tốc độ khi dữ liệu nhỏNhanh, độ trễ không đáng kể.Rất nhanh.Tốc độ khi dữ liệu lớnRất chậm,
gây nghẽn cổ chai (Bottleneck) mạng và ứng dụng.Rất nhanh, tận dụng được Index của Database.Bộ nhớ sử dụngTốn nhiều RAM máy chủ do phải tải hàng loạt Object thừa vào bộ nhớ.Tối ưu, chỉ cấp phát RAM cho danh sách đối tượng cuối cùng hợp lệ.
Khả năng bảo trìKhó khăn khi quy tắc lọc hoặc phân trang phức tạp lên.Gọn gàng, dễ bảo trì thông qua việc chèn thêm các mệnh đề .filter().Khả năng mở rộngKém, sụp đổ khi lượng dữ liệu lớn.Rất tốt.Phân tích chi tiết:Dễ hiểu hơn với người mới: 
Giải pháp dùng vòng lặp dễ tiếp cận hơn vì logic được xử lý bằng các lệnh if/else cơ bản của Python thay vì tư duy tập hợp của SQL.Tạo nhiều câu truy vấn hơn: Giải pháp dùng vòng lặp tạo ra vấn đề N+1 nghiêm trọng, liên tục "ping" xuống cơ sở dữ liệu để lấy thông tin của từng sinh viên.Khi có 1.000 sinh viên: 
Giải pháp JOIN là lựa chọn duy nhất phù hợp. Vòng lặp sẽ khiến API mất vài giây đến hàng chục giây chỉ để hoàn thành.Dễ thêm điều kiện lọc: Giải pháp JOIN vượt trội khi chỉ cần thêm điều kiện logic vào chuỗi Query mà không làm thay đổi cấu trúc vòng lặp.Nguy cơ gây chậm API:
Giải pháp vòng lặp có nguy cơ gây Crash và Timeout cho API khi lượng dữ liệu phình to theo thời gian.6.4. Lựa chọn giải phápGiải pháp được chọn: Giải pháp 2 - Sử dụng JOIN giữa Student và Enrollment.Lý do lựa chọn: Đây là best-practice cho việc xử lý dữ liệu quan hệ.
Cơ sở dữ liệu (MySQL) được sinh ra và tối ưu cực tốt cho các tác vụ lọc, loại trùng (DISTINCT) và sắp xếp (ORDER BY). Việc chuyển giao toàn bộ khối lượng tính toán này xuống CSDL giúp giải phóng tài nguyên CPU và RAM cho server API, giảm độ trễ mạng và loại bỏ tận gốc lỗi N+1 Query.Bối cảnh giải pháp còn lại phù hợp:
Giải pháp vòng lặp chỉ có giá trị khi thao tác với các hệ thống Microservices, nơi dữ liệu Student và Enrollment không nằm chung một Database vật lý, bắt buộc phải fetch dữ liệu thô về service trung gian để tự xử lý qua vòng lặp.Sự đánh đổi: Mã nguồn khó tiếp cận hơn với lập trình viên thiếu kinh nghiệm Database, 
đôi khi khó kiểm soát câu SQL sinh ra từ ORM nếu không bật log để kiểm tra cấu trúc.PHẦN 3: THIẾT KẾ VÀ TRIỂN KHAI6.5. Thiết kế các bước thực hiệnBước 1: Tiếp nhận Request. Lấy course_id từ đường dẫn URL của API.Bước 2: Xác thực Khóa học. Truy vấn bảng Course với ID tương ứng. Nếu kết quả là None,
lập tức ngắt luồng và trả về HTTPException(404).Bước 3: Xây dựng Query liên kết (JOIN). Mở phiên truy vấn đối tượng Student, dùng lệnh .join() trỏ sang bảng Enrollment.Bước 4: Áp dụng các bộ lọc (Filters). Áp dụng 3 điều kiện: ID khóa học khớp, trạng thái đăng ký là STUDYING hoặc COMPLETED,
trạng thái sinh viên là ACTIVE.Bước 5: Loại trùng và Sắp xếp. Gắn .distinct() để lọc bỏ các sinh viên có nhiều bản ghi đăng ký thỏa mãn và .order_by() theo cột họ tên.Bước 6: Tổng hợp dữ liệu. Tính total_students bằng hàm len().Bước 7: Trả về kết quả.
Ánh xạ dữ liệu thô vào CourseStudentsResponse Schema và trả về JSON chuẩn xác (hoặc mảng rỗng nếu không có sinh viên)."""


from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/training_system"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), default="ACTIVE")

    enrollments = relationship("Enrollment", back_populates="student")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="OPEN")

    enrollments = relationship("Enrollment", back_populates="course")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(String(50), nullable=False)

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class StudentSchema(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True

class CourseStudentsResponse(BaseModel):
    course_id: int
    course_name: str
    total_students: int
    students: List[StudentSchema]

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/courses/{course_id}/students", response_model=CourseStudentsResponse)
def get_students_by_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Khóa học không tồn tại")

    students = (
        db.query(Student)
        .join(Enrollment, Student.id == Enrollment.student_id)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status.in_(["STUDYING", "COMPLETED"]),
            Student.status == "ACTIVE"
        )
        .distinct()
        .order_by(Student.full_name.asc())
        .all()
    )

    return CourseStudentsResponse(
        course_id=course.id,
        course_name=course.name,
        total_students=len(students),
        students=students
    )