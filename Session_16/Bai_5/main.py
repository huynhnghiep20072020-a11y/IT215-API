"""1. Sơ đồ thực thể liên kết (ERD)
Mối quan hệ Nhiều - Nhiều (N-N) giữa Sinh viên và Buổi hội thảo không thể kết nối trực tiếp trong cơ sở dữ liệu quan hệ mà phải được phân rã thành hai mối quan hệ 1-N thông qua bảng trung gian vật lý Registration:

Student (1) - (N) Registration (N) - (1) Workshop

Mỗi Sinh viên (Student) có thể có nhiều lượt đăng ký (Registration).

Mỗi Workshop có thể chứa nhiều lượt đăng ký (Registration).

2. Xác định vị trí Khóa ngoại (ForeignKey)

Vị trí: Khóa ngoại được đặt tại bảng trung gian Registration (Bảng con - Child Table), bao gồm hai cột student_id và workshop_id.

Lý do về toàn vẹn dữ liệu: Trong quan hệ cơ sở dữ liệu, khóa ngoại bắt buộc nằm ở bảng mang ý nghĩa "Nhiều" (N).
Việc đặt khóa ngoại tại Registration tạo ra ràng buộc vật lý, đảm bảo rằng một lượt đăng ký không thể tồn tại nếu nó trỏ đến một mã student_id hoặc workshop_id không có thực trong hệ thống. 
Điều này ngăn chặn triệt để tình trạng sinh ra "dữ liệu rác".

3. Phân tích sự đánh đổi cấu hình (Tham số secondary vs Hai mối quan hệ 1-N)

Sử dụng tham số secondary (Cấu hình liên kết trực tiếp):

Ưu điểm: Cực kỳ tinh gọn ở tầng code logic. Lập trình viên có thể truy xuất thẳng đối tượng mục tiêu bằng cách gọi student.workshops hoặc workshop.students. SQLAlchemy sẽ tự động xử lý phép JOIN ngầm qua bảng trung gian.

Nhược điểm: Khó thao tác trực tiếp với các trường dữ liệu bổ sung nằm ở bảng trung gian (ví dụ: registered_at), vì lệnh gọi bỏ qua thực thể trung gian.

Truy xuất tuần tự qua hai mối quan hệ 1-N:

Ưu điểm: Quản lý và trích xuất được toàn bộ thông tin chi tiết của bảng trung gian (ví dụ: biết được sinh viên đăng ký vào thời gian nào).

Nhược điểm: Code dài dòng hơn. Để lấy danh sách workshop, lập trình viên phải gọi danh sách student.registrations, sau đó dùng vòng lặp duyệt qua từng đối tượng để lấy ra registration.workshop."""



