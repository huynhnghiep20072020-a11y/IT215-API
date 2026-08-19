import uuid
import re
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, status

app = FastAPI()

UPLOAD_DIR = Path("storage")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mock Database để kiểm tra trùng lặp (Bẫy 4, Rule)
MOCK_DB_APPLICATIONS = set()

# Hằng số
MAX_CV_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_AVATAR_SIZE = 3 * 1024 * 1024  # 3 MB
ALLOWED_CV_EXTS = {".pdf", ".docx"}
ALLOWED_AVATAR_EXTS = {".jpg", ".png"}

def validate_email(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        raise HTTPException(status_code=400, detail="Invalid email format")

async def save_file_with_chunking_and_limit(upload_file: UploadFile, dest_path: Path, max_size: int):
    """Hàm lưu file theo chunk và ngắt ngay nếu vượt dung lượng (Bẫy 2)"""
    bytes_written = 0
    chunk_size = 1024 * 1024  # 1 MB

    try:
        with open(dest_path, "wb") as f:
            while chunk := await upload_file.read(chunk_size):
                bytes_written += len(chunk)
                if bytes_written > max_size:
                    f.close()
                    dest_path.unlink() # Xóa file rác ghi dở
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File {upload_file.filename} exceeds size limit."
                    )
                f.write(chunk)
    except Exception as e:
        # Dọn dẹp nếu có lỗi I/O bất ngờ
        if dest_path.exists():
            dest_path.unlink()
        raise e

@app.post("/applications")
async def submit_application(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    cv: UploadFile = File(...),
    avatar: UploadFile = File(...)
):
    # 1. Validate Form & Business Rules
    validate_email(email)
    
    app_key = f"{email}_{position}"
    if app_key in MOCK_DB_APPLICATIONS:
        raise HTTPException(status_code=409, detail="Candidate already applied for this position")

    # 2. Validate Extensions
    cv_ext = Path(cv.filename).suffix.lower()
    avatar_ext = Path(avatar.filename).suffix.lower()

    if cv_ext not in ALLOWED_CV_EXTS:
        raise HTTPException(status_code=400, detail="CV must be PDF or DOCX")
    if avatar_ext not in ALLOWED_AVATAR_EXTS:
        raise HTTPException(status_code=400, detail="Avatar must be JPG or PNG")

    # 3. Generate Unique Names (Bẫy 4 - Ngăn file trùng tên)
    cv_safe_name = f"{uuid.uuid4().hex}_cv{cv_ext}"
    avatar_safe_name = f"{uuid.uuid4().hex}_avatar{avatar_ext}"
    
    cv_path = UPLOAD_DIR / cv_safe_name
    avatar_path = UPLOAD_DIR / avatar_safe_name

    # 4. Lưu CV trước
    await save_file_with_chunking_and_limit(cv, cv_path, MAX_CV_SIZE)

    # 5. Lưu Avatar và xử lý Rollback (Bẫy 3)
    try:
        await save_file_with_chunking_and_limit(avatar, avatar_path, MAX_AVATAR_SIZE)
    except Exception as e:
        # Nếu lưu Avatar lỗi (quá dung lượng hoặc I/O error), phải xóa CV đã lưu
        if cv_path.exists():
            cv_path.unlink()
        raise e

    # 6. Thành công: Ghi nhận hồ sơ
    MOCK_DB_APPLICATIONS.add(app_key)

    return {
        "success": True,
        "message": "Application submitted successfully",
        "data": {
            "name": full_name,
            "cv_path": str(cv_path),
            "avatar_path": str(avatar_path)
        }
    }