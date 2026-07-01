"""
Giải thích ngắn gọn:

Ứng dụng cung cấp 2 nhóm API: Quản lý phòng học (CRUD) và Quản lý đặt lịch.

Sử dụng Pydantic kết hợp thư viện enum để giới hạn các giá trị hợp lệ cho trường status của phòng và slot của ca học. Thư viện datetime được dùng để chuẩn hóa định dạng ngày tháng.

API GET /rooms tích hợp tìm kiếm và lọc qua Query Parameter không bắt buộc.

API POST /room-bookings áp dụng nhiều tầng validation chặt chẽ: kiểm tra phòng tồn tại (404), trạng thái AVAILABLE, sức chứa không bị vượt quá giới hạn và chặn đặt trùng (cùng id phòng, cùng ngày, cùng ca).
"""

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)