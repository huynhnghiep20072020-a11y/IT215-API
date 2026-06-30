"""
Phần 1: Phân tích & Đề xuất đa giải pháp

Input: Request body định dạng JSON chứa các trường thông tin của học viên (full_name, email, age, course, phone).
Output: Thông báo thành công kèm dữ liệu học viên (Status 200/201). Trả về lỗi 422 (Unprocessable Entity) nếu thiếu trường bắt buộc hoặc sai định dạng email. Trả về lỗi 400 (Bad Request) nếu email đã tồn tại.

Đề xuất 2 giải pháp validate:

Giải pháp 1: Nhận payload dưới dạng dict và tự viết các khối if/else thủ công kết hợp Regex để kiểm tra dữ liệu đầu vào.

Giải pháp 2: Sử dụng BaseModel của thư viện Pydantic kết hợp các class Field và EmailStr để framework tự động rà soát.

Phần 2: So sánh & Lựa chọn

Bảng so sánh:

Độ dễ hiểu: Giải pháp 1 (Phù hợp với tư duy kịch bản truyền thống) | Giải pháp 2 (Cần làm quen khái niệm OOP và Schema).

Số lượng code cần viết: Giải pháp 1 (Nhiều, dễ lặp lại) | Giải pháp 2 (Rất ít, tận dụng sức mạnh framework).

Khả năng kiểm soát lỗi: Giải pháp 1 (Dễ sai sót, thông báo lỗi phải tự cấu hình) | Giải pháp 2 (Tự động, chặn đứng lỗi ngay trước khi vào logic hàm, mã lỗi đồng nhất).

Độ rõ ràng của cấu trúc dữ liệu: Giải pháp 1 (Kém) | Giải pháp 2 (Rất rõ ràng, dễ bảo trì).

Lựa chọn: Chốt Giải pháp 2 (Sử dụng Pydantic). Đây là phương pháp tiêu chuẩn và mạnh mẽ nhất khi làm việc với FastAPI, giúp giải quyết triệt để Bẫy 1 (thiếu trường) và Bẫy 2 (sai định dạng email) hoàn toàn tự động mà không cần viết code logic thừa thãi, dành không gian hàm để xử lý Bẫy 3 (trùng lặp).

Phần 3: Thiết kế & Triển khai
"""

students_db = [
    {
        "full_name": "Nguyen Van A",
        "email": "existing@gmail.com",
        "age": 20,
        "course": "python",
        "phone": "0987654321"
    }
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)