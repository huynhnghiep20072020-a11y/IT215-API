"""Phân tích và đề xuất đa giải pháp cấu hình
6.1. Phân tích truy xuất quan hệVai trò của Khóa ngoại (ForeignKey): Khóa ngoại đóng vai trò tạo sự liên kết vật lý ở cấp độ cơ sở dữ liệu để đảm bảo tính toàn vẹn tham chiếu.
Nó ngăn chặn việc chèn các dữ liệu "rác" (ví dụ: đăng ký khóa học cho một sinh viên không tồn tại) và tự động xử lý các hành vi xóa/cập nhật liên đới.
Vị trí đặt Khóa ngoại: Trong mối quan hệ Nhiều - Nhiều (N-N), khóa ngoại bắt buộc phải được đặt ở bảng trung gian (cụ thể ở bài toán này là bảng Enrollment). 
Nguyên nhân là vì nếu đặt khóa ngoại ở bảng Student hay Course, ta sẽ vi phạm chuẩn hóa cơ sở dữ liệu đệ nhất (1NF), gây ra lỗi đa trị hoặc lặp lặp dữ liệu khổng lồ.
Tham số back_populates: Tham số này không bắt buộc phải giống tên bảng trong cơ sở dữ liệu. Bản chất của back_populates là khai báo tên của thuộc tính (attribute) relationship nằm ở class Model đối diện.
Nhiệm vụ của nó là giúp ORM của SQLAlchemy biết hai thuộc tính này đang tham chiếu lẫn nhau, từ đó tự động đồng bộ trạng thái của đối tượng ở cả hai chiều ngay trong bộ nhớ (session) mà không cần truy vấn lại CSDL.6.2. Đề xuất hai giải pháp cấu hình Model
Giải pháp 1 (Sử dụng liên kết trực tiếp qua tham số secondary): Ở giải pháp này, bảng trung gian Enrollment đóng vai trò là một "cây cầu" ẩn. Thuộc tính students trong Model Course và thuộc tính courses trong Model Student sẽ được khai báo hàm relationship() đi kèm tham số secondary="tên_bảng_trung_gian". 
SQLAlchemy sẽ tự động thực hiện phép JOIN ngầm định khi lập trình viên gọi thuộc tính, bỏ qua bước trung gian.Giải pháp 2 (Sử dụng liên kết gián tiếp thông qua hai quan hệ 1-N): Ở giải pháp này, ta phân rã hoàn toàn quan hệ N-N thành hai quan hệ 1-N riêng biệt. Model Enrollment đóng vai trò là bảng "Nhiều". Student có quan hệ 1-N với Enrollment, và Course có quan hệ 1-N với Enrollment.
Bảng trung gian lúc này hiện diện rõ ràng dưới dạng các đối tượng. Khi cần lấy danh sách sinh viên, ta không lấy trực tiếp được mà phải gọi course.enrollments, sau đó sử dụng vòng lặp duyệt qua từng đối tượng Enrollment để trích xuất student.Phần 2: So sánh và lựa chọn cấu hình6.3. Lập bảng so sánhTiêu chíGiải pháp 1 (Cấu hình secondary trực tiếp)Giải pháp 2 (Hai quan hệ 1-N song song)Độ ngắn gọn và tinh giản của codeCực kỳ ngắn gọn, 
chỉ cần gọi một thuộc tính ảo để lấy danh sách.Dài dòng hơn, đòi hỏi phải thao tác qua bảng trung gian.Cách truy xuất danh sách sinh viên từ đối tượng CourseTruy xuất trực tiếp: course.students (trả về thẳng list đối tượng Student).Phải dùng vòng lặp: [e.student for e in course.enrollments]Độ phức tạp khi cần đọc hiểu cấu trúc code đối với người mớiCần thời gian để hiểu cơ chế "ẩn bảng trung gian" của tham số secondary.Dễ hình dung vì mô hình ORM khớp chính xác 100% với các bước JOIN bảng trong SQL thuần.
Phân tích bổ sung:Giải pháp giúp lập trình viên viết code ngắn gọn nhất khi truy xuất dữ liệu liên kết là Giải pháp 1 (Cấu hình secondary).Trong thực tế học tập, Giải pháp 1 thường được khuyến khích sử dụng khi bảng trung gian chỉ làm nhiệm vụ liên kết thuần túy (chỉ chứa các khóa ngoại). Tuy nhiên, nếu bảng trung gian có thêm các cột dữ liệu mang ý nghĩa nghiệp vụ (như điểm số, ngày đăng ký), hệ thống sẽ cần đến cấu hình tương tự Giải pháp 2 (Association Object).6.4. Lựa chọn giải phápGiải pháp lựa chọn: 
Áp dụng mô hình kết hợp (Giải pháp 1 làm chủ đạo) nhưng khai báo tường minh Model Enrollment (Association Object) để đáp ứng trọn vẹn yêu cầu cấu trúc của bài toán.Lý do kỹ thuật:
Dựa vào bảng so sánh, Giải pháp 1 cung cấp khả năng tối ưu hóa truy xuất xuất sắc. 
Việc thiết lập secondary giúp mã nguồn logic xử lý trở nên cực kỳ gọn gàng (course.students). 
Đồng thời, để thỏa mãn điều kiện đề bài là khai báo 3 Model kế thừa Base và cấu hình thuộc tính cho cả 3 Model,
mô hình này cho phép vừa giữ được khả năng truy xuất trực tiếp danh sách sinh viên qua secondary,
vừa cho phép tương tác với dữ liệu chi tiết của bảng đăng ký.

Thiết kế các bước thực hiện

Khai báo lớp cơ sở Base bằng declarative_base().

Khai báo model Enrollment đại diện cho bảng trung gian, cấu hình hai ForeignKey trỏ đến students.id và courses.id,
đồng thời thiết lập hai thuộc tính relationship trỏ ngược về Student và Course.

Khai báo model Student với các cột thông tin cơ bản. 
Thiết lập thuộc tính enrollments (quan hệ 1-N) và thuộc tính courses sử dụng tham số secondary="enrollments" để vượt qua bảng trung gian,
tích hợp back_populates="students".

Khai báo model Course với các cột tương ứng. Thiết lập thuộc tính enrollments (quan hệ 1-N) 
và thuộc tính students sử dụng tham số secondary="enrollments" để lấy trực tiếp danh sách sinh viên, tích hợp back_populates="courses"."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Enrollment(Base):
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    
    enrollments = relationship("Enrollment", back_populates="student")
    courses = relationship("Course", secondary="enrollments", back_populates="students")


class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    enrollments = relationship("Enrollment", back_populates="course")
    students = relationship("Student", secondary="enrollments", back_populates="courses")