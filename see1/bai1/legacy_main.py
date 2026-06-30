from fastapi import FastAPI

app = FastAPI()

students = [
    {"id": 1, "name": "Nguyen Van A", "age": 20, "gpa": 3.5},
    {"id": 2, "name": "Tran Thi B",   "age": 21, "gpa": 3.8},
    {"id": 3, "name": "Le Van C",      "age": 19, "gpa": 3.2},
]

#  LEGACY CODE – chứa lỗi cần sinh viên phân tích và sửa
@app.get("/getStudents")
def getStudents():
    result = ""
    for s in students:
        result += str(s)   # nối dict thành chuỗi string thủ công
    return result          # trả về string thay vì JSON
