from fastapi import APIRouter, HTTPException, status
from typing import Optional
from schemas import StudentCreate, StudentUpdate
from data import students

router = APIRouter()

@router.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    for s in students:
        if s["code"] == student.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã học viên đã tồn tại"
            )
            
    new_id = max([s["id"] for s in students], default=0) + 1
    new_student = {
        "id": new_id,
        "code": student.code,
        "name": student.name,
        "email": student.email,
        "age": student.age
    }
    
    students.append(new_student)
    
    return {
        "message": "Thêm học viên thành công",
        "data": new_student
    }

@router.get("/students")
def get_students(
    keyword: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
):
    result = students
    
    if keyword is not None:
        kw = keyword.lower()
        result = [
            s for s in result
            if kw in s["name"].lower() or kw in s["code"].lower() or kw in s["email"].lower()
        ]
        
    if min_age is not None:
        result = [s for s in result if s["age"] >= min_age]
        
    if max_age is not None:
        result = [s for s in result if s["age"] <= max_age]
        
    return {
        "message": "Lấy danh sách học viên thành công",
        "data": result
    }

@router.get("/students/{student_id}")
def get_student_detail(student_id: int):
    target = next((s for s in students if s["id"] == student_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy học viên"
        )
        
    return {
        "message": "Lấy chi tiết học viên thành công",
        "data": target
    }

@router.put("/students/{student_id}")
def update_student(student_id: int, student_update: StudentUpdate):
    target = next((s for s in students if s["id"] == student_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy học viên"
        )
        
    for s in students:
        if s["code"] == student_update.code and s["id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã học viên đã tồn tại"
            )
            
    target["code"] = student_update.code
    target["name"] = student_update.name
    target["email"] = student_update.email
    target["age"] = student_update.age
    
    return {
        "message": "Cập nhật học viên thành công",
        "data": target
    }

@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    for index, s in enumerate(students):
        if s["id"] == student_id:
            deleted_student = students.pop(index)
            return {
                "message": "Xóa học viên thành công",
                "data": deleted_student
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Không tìm thấy học viên"
    )