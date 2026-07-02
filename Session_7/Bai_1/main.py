"""Phần 1: Chỉ ra lỗi bằng test case cụ thể
STTDữ liệu gửi lênKết quả hiện tại (Mã HTTP + Body)Kết quả đúng mong muốnLỗi phát hiện1order_id = 999HTTP 200 OK.
Body: {"message": "Order not found"}HTTP 404 Not Found. Body: {"detail": "Order not found"}Không dùng HTTPException.
Báo lỗi nhưng vẫn trả về mã 200 OK (Lỗi trạng thái ảo).2order_id = 1HTTP 200 OK. Body chứa cả profit_margin và supplier_id.HTTP 200 OK.
Body chỉ chứa id, customer_name, total_amount.Lộ dữ liệu nhạy cảm do trả về trực tiếp dữ liệu thô mà không thông qua Response Model để lọc.
Phần 2: Sửa lại source codeTách code thành các file độc lập.Tạo class OrderPublic đóng vai trò là DTO (Data Transfer Object) để loại bỏ 2 trường nhạy cảm, 
tích hợp vào response_model.Sử dụng raise HTTPException với status code 404 để xử lý tình huống không tìm thấy dữ liệu chuẩn RESTful."""

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)