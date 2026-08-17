from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "customer"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class TransferRequest(BaseModel):
    to_username: str
    amount: float = Field(..., gt=0)
    note: Optional[str] = ""

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    balance: float
    created_at: datetime
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"