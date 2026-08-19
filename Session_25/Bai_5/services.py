import uuid
import re
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
import logging

from database import file_metadata_db

STORAGE_DIR = Path("storage")
CV_DIR = STORAGE_DIR / "cvs"
AVATAR_DIR = STORAGE_DIR / "avatars"

# Khởi tạo thư mục
for directory in [CV_DIR, AVATAR_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "cv": {".pdf", ".docx"},
    "avatar": {".jpg", ".png"}
}
MAX_SIZES = {
    "cv": 5 * 1024 * 1024,      # 5MB
    "avatar": 2 * 1024 * 1024   # 2MB
}
ALLOWED_POSITIONS = ["backend", "frontend", "designer", "hr"]

def validate_form_data(full_name: str, email: str, phone: str, position: str):
    # 1. Chặn chuỗi chỉ chứa khoảng trắng và chuẩn hóa
    name_clean = full_name.strip().title()
    email_clean = email.strip()
    phone_clean = phone.strip()
    pos_clean = position.strip().lower()

    if not name_clean or not email_clean or not phone_clean:
        raise HTTPException(status_code=400, detail="Required fields cannot be empty or just spaces.")
    
    # 2. Kiểm tra Email hợp lệ
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_clean):
        raise HTTPException(status_code=400, detail="Invalid email format.")

    # 3. Kiểm tra loại tài liệu/vị trí
    if pos_clean not in ALLOWED_POSITIONS:
        raise HTTPException(status_code=400, detail=f"Position must be one of {ALLOWED_POSITIONS}")

    return name_clean

async def save_file_safely(file: UploadFile, file_category: str) -> dict:
    """Lưu file an toàn bằng chunking, trả về metadata tạm."""
    if not file.filename:
        raise HTTPException(status_code=400, detail=f"Nameless file detected for {file_category}.")

    # Xử lý tên file chứa nhiều dấu chấm, chỉ lấy đuôi cuối cùng (vd: malware.pdf.exe -> .exe)
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS[file_category]:
        raise HTTPException(status_code=400, detail=f"Invalid extension for {file_category}. Allowed: {ALLOWED_EXTENSIONS[file_category]}")

    # Sinh tên file duy nhất chống ghi đè
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"
    
    target_dir = CV_DIR if file_category == "cv" else AVATAR_DIR
    file_path = target_dir / safe_filename

    # Đọc và ghi theo chunk để kiểm soát dung lượng, tránh tràn RAM
    bytes_written = 0
    chunk_size = 1024 * 1024 # 1MB
    limit_size = MAX_SIZES[file_category]

    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(chunk_size):
                bytes_written += len(chunk)
                if bytes_written > limit_size:
                    f.close()
                    file_path.unlink() # Xóa file rác
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"{file_category.upper()} file exceeds limit of {limit_size // (1024*1024)}MB."
                    )
                f.write(chunk)
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise e

    if bytes_written == 0:
        file_path.unlink()
        raise HTTPException(status_code=400, detail=f"Empty file detected for {file_category}.")

    return {
        "file_id": file_id,
        "original_name": Path(file.filename).name, # Chỉ lấy tên, bỏ qua đường dẫn lạ nếu có
        "saved_name": safe_filename,
        "file_type": file_category,
        "size_bytes": bytes_written,
        "upload_time": datetime.now().isoformat(),
        "path": str(file_path)
    }

def process_rollback(temp_records: list):
    """Xóa các file đã lưu nếu có bước bị lỗi."""
    for record in temp_records:
        path = Path(record["path"])
        if path.exists():
            path.unlink()
            logging.info(f"Rollback: Deleted {path}")