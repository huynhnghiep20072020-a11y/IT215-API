from fastapi import FastAPI
import typing

app = FastAPI(title="Student Management API", version="1.0.0")

# Dữ liệu mẫu (trong thực tế sẽ lấy từ database)
students = [
    {"id": 1, "name": "Nguyen Van A", "age": 20, "gpa": 3.5},
    {"id": 2, "name": "Tran Thi B",   "age": 21, "gpa": 3.8},
    {"id": 3, "name": "Le Van C",      "age": 19, "gpa": 3.2},
]

#  FIXED CODE – đúng chuẩn RESTful, trả về JSON list
@app.get("/students")           #  Đường dẫn RESTful: danh từ số nhiều, chữ thường
def get_students() -> typing.List[dict]:
    """Trả về danh sách toàn bộ sinh viên dưới dạng JSON array."""
    return students             #  FastAPI tự serialize list[dict] → JSON array
