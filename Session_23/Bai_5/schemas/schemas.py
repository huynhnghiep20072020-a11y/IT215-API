from pydantic import BaseModel
from typing import Optional

class AssignmentCreate(BaseModel):
    title: str
    description: str

class SubmissionCreate(BaseModel):
    assignment_id: int
    content_url: str

class GradeUpdate(BaseModel):
    score: float