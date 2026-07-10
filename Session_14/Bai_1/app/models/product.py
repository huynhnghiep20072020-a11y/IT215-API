from sqlalchemy import Column, Integer,String,Float
from app.database import Base
class Product(Base):
    __tablenname__="products"
    id = Column(Integer, primary_key=True,index=True)
    name =Column(String(255),Nullable=False)
    price =Column(Float,nullable=False)
    