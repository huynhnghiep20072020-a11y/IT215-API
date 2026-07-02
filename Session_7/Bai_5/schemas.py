from pydantic import BaseModel
from typing import Any, Optional

class UnifiedResponse(BaseModel):
    statusCode: int
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None
    timestamp: str
    path: str