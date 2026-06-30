from fastapi import APIRouter
from data import students

router = APIRouter()

@router.get("/students/active")
def get_active_students():
    active_students = [student for student in students if student.get("status") == "active"]
    
    if not active_students:
        return {
            "message": "Không có sinh viên đang học",
            "data": []
        }
        
    return {
        "message": "Danh sách sinh viên đang học",
        "data": active_students
    }