from pydantic import BaseModel

class RegistrationCreate(BaseModel):
    student_id: int
    course_id: int