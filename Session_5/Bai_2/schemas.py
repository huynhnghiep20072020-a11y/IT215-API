from pydantic import BaseModel

class EnrollmentCreate(BaseModel):
    student_id: str
    course_id: int