from pydantic import BaseModel

class OrderPublic(BaseModel):
    id: int
    customer_name: str
    total_amount: float