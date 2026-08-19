import os
import re
import uuid
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, status

app = FastAPI(title="Student Submission API")

# --- MOCK DATA ---
assignments = {
    1: {
        "id": 1,
        "title": "FastAPI CRUD",
        "deadline": "2026-08-15T23:59:59",
        "allowed_extensions": [".zip", ".pdf"],
        "max_size_mb": 20,
        "is_open": True,
    },
    2: {
        "id": 2,
        "title": "Python Final Project",
        "deadline": "2026-07-20T23:59:59",
        "allowed_extensions": [".zip"],
        "max_size_mb": 50,
        "is_open": False,
    },
}

# Theo dõi số lần nộp: {(student_id, assignment_id): attempts_count}
submissions_record = {}

# --- HELPER FUNCTIONS ---

def validate_student_data(student_id: str, student_name: str) -> str:
    """Kiểm tra định dạng sinh viên"""
    name_stripped = student_name.strip()
    if not name_stripped:
        raise HTTPException(status_code=400, detail="Student name cannot be empty")
    
    if not re.match(r"^SV\d{6}$", student_id):
        raise HTTPException(status_code=400, detail="Invalid student_id format. Must be SV followed by 6 digits.")
    
    return name_stripped

def validate_assignment(assignment_id: int):
    """Kiểm tra bài tập tồn tại, trạng thái và deadline (Bẫy 1, Bẫy 2)"""
    if assignment_id not in assignments:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    task = assignments[assignment_id]
    if not task["is_open"]:
        raise HTTPException(status_code=409, detail="Assignment is closed")
    
    deadline = datetime.fromisoformat(task["deadline"])
    if datetime.now() > deadline:
        raise HTTPException(status_code=409, detail="Submission deadline has passed")
    
    return task

def get_and_check_attempt(student_id: str, assignment_id: int) -> int:
    """Đếm số lần nộp và kiểm tra giới hạn (Bẫy 3)"""
    current_attempts = submissions_record.get((student_id, assignment_id), 0)
    if current_attempts >= 3:
        raise HTTPException(status_code=409, detail="Maximum number of attempts (3) reached")
    return current_attempts + 1

def validate_file_and_get_content(file: UploadFile, allowed_exts: list, max_mb: int) -> tuple[bytes, str]:
    """Kiểm tra file: rỗng, đuôi mở rộng, kích thước (Bẫy 5, Bẫy 6)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Invalid file extension. Allowed: {', '.join(allowed_exts)}")
    
    # Đọc dữ liệu để kiểm tra kích thước
    # Do FastAPI UploadFile.read() là async nên phải tách phần async ra ngoài hoặc dùng read đồng bộ (nếu file đã spool).
    # Tuy nhiên, ta sẽ truyền content từ endpoint vào hàm này để kiểm tra cho dễ.
    pass

def generate_safe_path(student_id: str, assignment_id: int, attempt: int, ext: str) -> tuple[Path, str]:
    """Tạo thư mục và sinh tên file an toàn (Bẫy 4)"""
    random_str = uuid.uuid4().hex[:8]
    safe_filename = f"{student_id}_assignment_{assignment_id}_attempt_{attempt}_{random_str}{ext}"
    
    dir_path = Path(f"storage/submissions/assignment_{assignment_id}/{student_id}/")
    dir_path.mkdir(parents=True, exist_ok=True)
    
    return dir_path / safe_filename, safe_filename

def save_file_safely(file_path: Path, content: bytes):
    """Lưu file và dọn dẹp nếu thất bại (Bẫy 7)"""
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Failed to write file: {e}")
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Internal server error during file save")

# --- MAIN ENDPOINT ---

@app.post("/api/submissions")
async def submit_assignment(
    student_id: str = Form(...),
    student_name: str = Form(...),
    assignment_id: int = Form(...),
    note: str = Form(None),
    submission_file: UploadFile = File(...)
):
    # 1. Kiểm tra thông tin sinh viên
    valid_name = validate_student_data(student_id, student_name)
    
    # 2. Kiểm tra bài tập (Bẫy 1, 2)
    task = validate_assignment(assignment_id)
    
    # 3. Đếm số lần nộp (Bẫy 3)
    attempt = get_and_check_attempt(student_id, assignment_id)
    
    # 4. Kiểm tra thuộc tính cơ bản của file (Bẫy 5)
    if not submission_file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    ext = Path(submission_file.filename).suffix.lower()
    if ext not in task["allowed_extensions"]:
        raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed.")
        
    # Đọc file và kiểm tra kích thước (Bẫy 6)
    content = await submission_file.read()
    file_size_bytes = len(content)
    
    if file_size_bytes == 0:
        raise HTTPException(status_code=400, detail="File is empty")
        
    if file_size_bytes > task["max_size_mb"] * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {task['max_size_mb']}MB")
    
    # 5. Sinh đường dẫn an toàn (Bẫy 4)
    file_path, stored_filename = generate_safe_path(student_id, assignment_id, attempt, ext)
    
    # 6. Lưu file an toàn (Bẫy 7)
    save_file_safely(file_path, content)
    
    # 7. Ghi nhận thành công
    submissions_record[(student_id, assignment_id)] = attempt
    
    return {
        "success": True,
        "message": "Submission uploaded successfully",
        "data": {
            "student_id": student_id,
            "assignment_id": assignment_id,
            "attempt": attempt,
            "original_filename": Path(submission_file.filename).name,
            "stored_filename": stored_filename,
            "file_size": file_size_bytes,
            "submitted_at": datetime.now().isoformat()
        }
    }