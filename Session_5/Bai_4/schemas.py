from pydantic import BaseModel, Field

class ProductUpdate(BaseModel):
    code: str
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)