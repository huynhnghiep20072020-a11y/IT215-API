"""XÁC ĐỊNH QUAN HỆ
1. Bảng phân loại quan hệ
Hai đối tượngLoại quan hệ
Department – Student1-N (Một - Nhiều)
Student – CourseN-N (Nhiều - Nhiều)
2. Trả lời câu hỏi thiết kếKhóa ngoại liên kết sinh viên với phòng ban đặt ở đâu?Khóa ngoại 
(department_id) bắt buộc phải được đặt ở bảng Student (danh sách sinh viên), vì đây là thực thể mang ý nghĩa "Nhiều" trong mối quan hệ 1-N.
Quan hệ giữa sinh viên và khóa học cần danh sách trung gian nào?Cần danh sách trung gian là enrollments (danh sách đăng ký) để lưu trữ các cặp khóa ngoại student_id và course_id."""


from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

departments = [
    {"id": 1, "name": "Khoa Công nghệ thông tin"},
    {"id": 2, "name": "Khoa Kinh tế"}
]

students = [
    {"id": 1, "full_name": "Nguyễn Văn A", "status": "ACTIVE", "department_id": 1},
    {"id": 2, "full_name": "Trần Thị B", "status": "INACTIVE", "department_id": 2}
]

courses = [
    {"id": 1, "name": "Lập trình Python", "status": "OPEN"},
    {"id": 2, "name": "Xây dựng Web API", "status": "OPEN"},
    {"id": 3, "name": "Cơ sở dữ liệu nâng cao", "status": "CLOSED"}
]

enrollments = [
    {"id": 1, "student_id": 1, "course_id": 1}
]

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

@app.get("/students/{student_id}")
def get_student_details(student_id: int):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên.")

    department = next((d for d in departments if d["id"] == student["department_id"]), None)

    student_enrollments = [e for e in enrollments if e["student_id"] == student_id]
    
    enrolled_courses = []
    for e in student_enrollments:
        course = next((c for c in courses if c["id"] == e["course_id"]), None)
        if course:
            enrolled_courses.append(course)

    return {
        "student": student,
        "department": department,
        "courses": enrolled_courses
    }

@app.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment_data: EnrollmentCreate):
    student = next((s for s in students if s["id"] == enrollment_data.student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Sinh viên không tồn tại.")
        
    if student["status"] != "ACTIVE":
        raise HTTPException(status_code=400, detail="Sinh viên đang ở trạng thái INACTIVE.")

    course = next((c for c in courses if c["id"] == enrollment_data.course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Khóa học không tồn tại.")
        
    if course["status"] != "OPEN":
        raise HTTPException(status_code=400, detail="Khóa học đã đóng, không thể đăng ký.")

    is_duplicate = any(
        e["student_id"] == enrollment_data.student_id and e["course_id"] == enrollment_data.course_id
        for e in enrollments
    )
    if is_duplicate:
        raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký khóa học này rồi.")

    new_id = max((e["id"] for e in enrollments), default=0) + 1
    
    new_enrollment = {
        "id": new_id,
        "student_id": enrollment_data.student_id,
        "course_id": enrollment_data.course_id
    }
    
    enrollments.append(new_enrollment)
    
    return new_enrollment