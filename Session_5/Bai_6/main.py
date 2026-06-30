products = [
    {"id": 1, "name": "Keyboard", "price": 500000},
    {"id": 2, "name": "Mouse", "price": 300000}
]

from fastapi import FastAPI
import routers

app = FastAPI()

app.include_router(routers.router)