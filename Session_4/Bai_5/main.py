"""


Sử dụng thư viện pydantic để tạo class StudentRegister kiểm tra tự động các ràng buộc dữ liệu: min_length (tên, số điện thoại), ge/le (tuổi từ 15-60), pattern (chỉ chứa số cho số điện thoại), và EmailStr (định dạng email chuẩn).

Áp dụng yêu cầu sáng tạo: Tạo tự động mã học viên ngẫu nhiên (VD: HV-12345) và chuẩn hóa dữ liệu đầu vào trước khi trả về (viết hoa chữ cái đầu của tên, viết thường email và ghi chú).

Code được chia thành 3 file: schemas.py (chứa cấu trúc dữ liệu), routers.py (chứa logic xử lý API) và main.py (chạy ứng dụng).
"""

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)