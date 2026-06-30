from fastapi import APIRouter, HTTPException, status
from schemas import RegistrationCreate
from data import students, courses, registrations

router = APIRouter()

@router.post("/registrations", status_code=status.HTTP_201_CREATED)
def create_registration(reg: RegistrationCreate):
    student_exists = any(s["id"] == reg.student_id for s in students)
    if not student_exists:
        raise HTTPException(status_code=404, detail="Student not found")

    course = next((c for c in courses if c["id"] == reg.course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    for existing_reg in registrations:
        if existing_reg["student_id"] == reg.student_id and existing_reg["course_id"] == reg.course_id:
            raise HTTPException(status_code=400, detail="Student already registered this course")

    current_enrollments = sum(1 for r in registrations if r["course_id"] == reg.course_id)
    if current_enrollments >= course["capacity"]:
        raise HTTPException(status_code=400, detail="Course is full")

    new_reg = {
        "id": len(registrations) + 1,
        "student_id": reg.student_id,
        "course_id": reg.course_id
    }
    
    registrations.append(new_reg)

    return {
        "message": "Registration successful",
        "data": new_reg
    }