from sqlalchemy import Column, String, Float, Integer
from database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(50), primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    daily_rate = Column(Float, nullable=False)
    production_year = Column(Integer, nullable=False)
    status = Column(String(20), default="available", nullable=False)