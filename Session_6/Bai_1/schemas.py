from pydantic import BaseModel, Field

class CourseBase(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    duration: int = Field(..., gt=0)
    fee: float = Field(..., ge=0)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass