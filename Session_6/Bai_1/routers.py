from fastapi import APIRouter, HTTPException, status
from typing import Optional
from schemas import CourseCreate, CourseUpdate
from data import courses

router = APIRouter()

@router.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate):
    for c in courses:
        if c["code"] == course.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã khóa học đã tồn tại"
            )

    new_id = max([c["id"] for c in courses], default=0) + 1
    new_course = {
        "id": new_id,
        "code": course.code,
        "name": course.name,
        "duration": course.duration,
        "fee": course.fee
    }
    courses.append(new_course)
    
    return {
        "message": "Thêm khóa học thành công",
        "data": new_course
    }

@router.get("/courses")
def get_courses(
    keyword: Optional[str] = None, 
    min_fee: Optional[float] = None, 
    max_fee: Optional[float] = None
):
    result = courses

    if keyword is not None:
        kw = keyword.lower()
        result = [
            c for c in result 
            if kw in c["name"].lower() or kw in c["code"].lower()
        ]

    if min_fee is not None:
        result = [c for c in result if c["fee"] >= min_fee]

    if max_fee is not None:
        result = [c for c in result if c["fee"] <= max_fee]

    return {
        "message": "Lấy danh sách khóa học thành công",
        "data": result
    }

@router.get("/courses/{course_id}")
def get_course_detail(course_id: int):
    target = next((c for c in courses if c["id"] == course_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy khóa học"
        )
        
    return {
        "message": "Lấy chi tiết khóa học thành công",
        "data": target
    }

@router.put("/courses/{course_id}")
def update_course(course_id: int, course_update: CourseUpdate):
    target = next((c for c in courses if c["id"] == course_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy khóa học"
        )

    for c in courses:
        if c["code"] == course_update.code and c["id"] != course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã khóa học đã tồn tại"
            )

    target["code"] = course_update.code
    target["name"] = course_update.name
    target["duration"] = course_update.duration
    target["fee"] = course_update.fee

    return {
        "message": "Cập nhật khóa học thành công",
        "data": target
    }

@router.delete("/courses/{course_id}")
def delete_course(course_id: int):
    for index, c in enumerate(courses):
        if c["id"] == course_id:
            deleted_course = courses.pop(index)
            return {
                "message": "Xóa khóa học thành công",
                "data": deleted_course
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Không tìm thấy khóa học"
    )