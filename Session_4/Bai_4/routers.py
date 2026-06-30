from fastapi import APIRouter, HTTPException
from schemas import StudentCreate
from data import students_db

router = APIRouter()

@router.post("/students")
def create_student(student: StudentCreate):
    for existing_student in students_db:
        if existing_student["email"] == student.email:
            raise HTTPException(status_code=400, detail="Email đã tồn tại trong hệ thống")
            
    new_student = student.model_dump()
    students_db.append(new_student)
    
    return {
        "message": "Thêm học viên thành công",
        "data": new_student
    }