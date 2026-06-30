from pydantic import BaseModel

class ProductCreate(BaseModel):
    code: str
    name: str
    price: float
    stock: int