from fastapi import APIRouter
from schemas import StudentRegister
import random

router = APIRouter()

@router.post("/students/register")
def register_student(student: StudentRegister):
    student_code = f"HV-{random.randint(10000, 99999)}"
    
    standardized_full_name = student.full_name.title()
    standardized_email = student.email.lower()
    standardized_note = student.note.lower() if student.note else None

    response_data = {
        "student_code": student_code,
        "full_name": standardized_full_name,
        "email": standardized_email,
        "age": student.age,
        "phone": student.phone,
        "course": student.course,
        "note": standardized_note
    }

    return {
        "message": "Đăng ký học viên thành công",
        "data": response_data
    }