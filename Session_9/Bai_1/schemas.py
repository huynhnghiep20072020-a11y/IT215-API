from pydantic import BaseModel, Field

class TaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=1)
    assignee: str = Field(..., min_length=1)
    priority: int = Field(..., ge=1, le=5)

class TaskStatusUpdateSchema(BaseModel):
    status: str = Field(..., min_length=1)