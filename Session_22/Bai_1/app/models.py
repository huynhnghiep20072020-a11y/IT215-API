from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="customer")
    balance = Column(Float, default=10000.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))