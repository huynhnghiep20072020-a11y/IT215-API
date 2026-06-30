from fastapi import APIRouter
from typing import Optional
from data import courses

router = APIRouter()

@router.get("/courses")
def get_all_courses():
    return {
        "message": "Lấy danh sách khóa học thành công",
        "data": courses
    }

@router.get("/courses/search")
def search_courses(mode: Optional[str] = None, category: Optional[str] = None):
    result = courses
    
    if mode is not None:
        result = [course for course in result if course.get("mode") == mode]
        
    if category is not None:
        result = [course for course in result if course.get("category") == category]
        
    return {
        "message": "Lấy danh sách khóa học thành công",
        "data": result
    }

@router.get("/courses/{course_id}")
def get_course_detail(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return {
                "message": "Tìm thấy khóa học",
                "data": course
            }
            
    return {
        "message": "Không tìm thấy khóa học"
    }