"""

Input: Danh sách các dictionary chứa thông tin sách.

Output: Dữ liệu JSON có cấu trúc gồm "message" và "data" (danh sách sách thỏa mãn điều kiện).

Điều kiện: Sách phải có trường "quantity", và 0 <= quantity <= 5.

Phần 2: Đề xuất giải pháp

Giải pháp 1: Sử dụng vòng lặp for truyền thống kết hợp câu lệnh if / continue.

Giải pháp 2: Sử dụng list comprehension kết hợp logic điều kiện trên một dòng.

Phần 3: So sánh và lựa chọn giải pháp

Vòng lặp for: Độ dễ hiểu (Cao), Độ ngắn gọn (Thấp), Dễ xử lý bẫy (Rất tốt), Dễ bảo trì (Cao).

List comprehension: Độ dễ hiểu (Thấp), Độ ngắn gọn (Cao), Dễ xử lý bẫy (Khó, code sẽ rất rối), Dễ bảo trì (Trung bình).
=> Lựa chọn: Giải pháp 1 (Vòng lặp for) vì các bẫy dữ liệu (thiếu key, số âm) được bóc tách xử lý rõ ràng, an toàn và dễ bảo trì hơn.

Phần 4: Thiết kế luồng xử lý

Khởi tạo router/app với endpoint GET /books/low-stock.

Khởi tạo một mảng rỗng để chứa sách hợp lệ.

Duyệt qua từng sách trong danh sách: bỏ qua nếu thiếu "quantity", bỏ qua nếu "quantity" < 0, thêm vào mảng nếu "quantity" <= 5.

Nếu mảng rỗng thì trả về thông báo không có sách. Ngược lại trả về danh sách đã lọc.
"""


books = [
    {"id": 1, "title": "Python Basic", "quantity": 12},
    {"id": 2, "title": "FastAPI Beginner", "quantity": 3},
    {"id": 3, "title": "Clean Code", "quantity": 5},
    {"id": 4, "title": "Database Design", "quantity": 0},
    {"id": 5, "title": "Web API Design", "quantity": 20},
    {"id": 6, "title": "Java Basic"},
    {"id": 7, "title": "Spring Boot", "quantity": -2}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)