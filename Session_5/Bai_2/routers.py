from fastapi import APIRouter, HTTPException, status
from schemas import EnrollmentCreate
from data import enrollments

router = APIRouter()

@router.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment: EnrollmentCreate):
    for e in enrollments:
        if e["student_id"] == enrollment.student_id and e["course_id"] == enrollment.course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Học viên đã đăng ký khóa học này rồi"
            )

    new_enrollment = {
        "id": len(enrollments) + 1,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id
    }
    
    enrollments.append(new_enrollment)
    
    return {
        "message": "Enroll successfully",
        "data": new_enrollment
    }