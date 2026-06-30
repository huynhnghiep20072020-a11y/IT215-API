"""Phần 1: Chỉ ra lỗi bằng test case cụ thểSTTDữ liệu gửi lên (Request Body)Kết quả hiện tại (Lỗi)Kết quả đúng mong muốnLỗi phát hiện1{"code": "SP001", "name": "Bàn phím", "price": 500000, "stock": 10}
Vẫn tạo được sản phẩm mới với mã SP001.Báo lỗi mã sản phẩm đã tồn tại (HTTP 400).Không kiểm tra trùng lặp mã code trước khi thêm vào danh sách.2{"code": "SP003", "name": "Tai nghe", "price": 350000, "stock": 20}Tạo thành công nhưng trả về HTTP status 200 OK mặc định.Tạo thành công và trả về HTTP status 201 Created.
API chưa được cấu hình trả về mã trạng thái 201 chuẩn RESTful khi tạo mới.Phần 2: Sửa lại source codeTách dự án thành các file riêng biệt để dễ quản lý.Thêm logic kiểm tra trùng code bằng vòng lặp, nếu trùng sẽ ném ra HTTPException.Cấu hình status_code=status.HTTP_201_CREATED cho route POST."""

products = [
    {
        "id": 1,
        "code": "SP001",
        "name": "Laptop Dell",
        "price": 15000000,
        "stock": 10
    },
    {
        "id": 2,
        "code": "SP002",
        "name": "Mouse Logitech",
        "price": 350000,
        "stock": 50
    }
]
from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)