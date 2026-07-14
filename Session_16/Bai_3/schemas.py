from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True

class CourseBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StudentCoursesResponse(BaseModel):
    student_id: int = Field(validation_alias="id")
    full_name: str
    courses: List[CourseBasic]

    class Config:
        from_attributes = True
        populate_by_name = True