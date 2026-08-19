from fastapi import FastAPI
from routers import router

app = FastAPI(title="Recruio Application Portal")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to Recruio API. Visit /docs for Swagger UI."}