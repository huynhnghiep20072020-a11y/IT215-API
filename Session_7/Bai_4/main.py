"""
Phần 1: Phân tích & Đề xuất đa giải pháp
Phân tích Input/Output:Input: order_id (số nguyên) được truyền qua Path Parameter.
Output thành công: Trạng thái HTTP 200 OK kèm thông tin thanh toán (payment_status, method).
Output thất bại: Trạng thái HTTP 404 Not Found (nếu sai ID) hoặc HTTP 500 Internal Server Error 
(nếu có lỗi logic nội bộ, thông báo đã được làm sạch, không lộ stack trace).
Đề xuất 2 giải pháp:Giải pháp 1 (List): Dùng vòng lặp for để duyệt tuần tự qua từng phần tử trong mảng cho đến khi tìm thấy ID tương ứng.
Giải pháp 2 (Dict): Chuyển đổi cấu trúc dữ liệu sang dạng Bảng băm (Dictionary) với Key chính là order_id để truy xuất trực tiếp.
Phần 2: So sánh & Lựa chọn giải pháp
Tiêu chí	Giải pháp 1: Duyệt List	Giải pháp 2: Dùng Dict
Tốc độ tìm kiếm	Chậm, độ phức tạp O(N)	Cực nhanh, độ phức tạp O(1)
Bộ nhớ tiêu hao	Thấp hơn	Cao hơn một chút (do cấp phát không gian cho Hash Table)
Độ dễ hiểu	Quen thuộc với người mới học	Gọn gàng, rành mạch
Khả năng bảo trì	Code tìm kiếm thường dài dòng hơn	Code ngắn gọn, dễ dàng mở rộng
Bối cảnh phù hợp	Dữ liệu rất nhỏ, tần suất truy vấn ít	Dữ liệu lớn (hàng vạn đơn hàng), truy vấn liên tục
Kết luận: Lựa chọn Giải pháp 2 (Dùng Dict) vì hệ thống phát sinh hàng vạn đơn hàng mỗi ngày.
Việc dùng Key (order_id) truy xuất trực tiếp giúp loại bỏ độ trễ (Latency),
tối ưu hóa hiệu năng cực hạn so với việc duyệt mảng tuyến tính.

"""
from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)