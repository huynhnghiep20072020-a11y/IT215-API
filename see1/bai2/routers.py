from fastapi import APIRouter
from data import students

router = APIRouter()

@router.get("/students")
def get_all_students():
    return students
