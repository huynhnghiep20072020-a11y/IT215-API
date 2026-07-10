from fastapi import  FastAPI
from app.database import engine,Base
from app.routers import product

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(product.router)
