"""Phần 1: Chỉ ra lỗi bằng test case cụ thể
STTDữ liệu/Endpoint gửi lênKết quả hiện tại (Mã HTTP + Body)Kết quả đúng mong muốnLỗi phát hiện1PUT /orders/999/status với status="SHIPPING"HTTP 200 OK.
Body: {"statusCode": 200, "message": "Cập nhật thành công", "data": null}HTTP 404 Not Found. Body: {"detail": "Order not found"}Báo lỗi bằng lệnh print ra console thay vì trả về client,
không ngắt luồng xử lý khiến hàm tiếp tục chạy và trả về mã 200 (lỗi trạng thái ảo).2PUT /orders/1/status với status="TRONG_SANG"HTTP 200 OK. Body: {"error": "Trạng thái không hợp lệ"}HTTP 400 Bad Request.
Body: {"detail": "Trạng thái không hợp lệ"}Sử dụng return cho luồng lỗi khiến API vẫn trả về mã 200 OK. Vi phạm nguyên tắc "Sai thì raise".
Ngoài ra, code cũ sử dụng Magic Number (200) cứng trong logic.
Phần 2: Sửa lại source codeTách dự án thành các file độc lập.
Áp dụng nguyên tắc "Sai thì raise" bằng HTTPException để ngắt luồng ngay khi phát hiện dữ liệu không hợp lệ
(sai ID hoặc sai trạng thái).Loại bỏ các "Magic Number" bằng cách sử dụng module status của FastAPI
(status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST)."""

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)