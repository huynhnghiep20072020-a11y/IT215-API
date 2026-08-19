from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from services import validate_form_data, save_file_safely, process_rollback, STORAGE_DIR
from database import file_metadata_db

router = APIRouter()

@router.post("/files/upload", status_code=201)
async def upload_application(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    portfolio_url: str = Form(None), # Trường không bắt buộc
    cv: UploadFile = File(...),
    avatar: UploadFile = File(...)
):
    # 1. Chuẩn hóa và Validate Form
    normalized_name = validate_form_data(full_name, email, phone, position)

    temp_records = []
    try:
        # 2. Lưu CV (có kiểm tra giới hạn)
        cv_record = await save_file_safely(cv, "cv")
        temp_records.append(cv_record)

        # 3. Lưu Avatar (có kiểm tra giới hạn)
        avatar_record = await save_file_safely(avatar, "avatar")
        temp_records.append(avatar_record)

        # 4. Ghi nhận thành công vào Database
        file_metadata_db[cv_record["file_id"]] = cv_record
        file_metadata_db[avatar_record["file_id"]] = avatar_record

        return {
            "success": True,
            "message": "Application and files uploaded successfully.",
            "candidate": {
                "normalized_name": normalized_name,
                "email": email.strip()
            },
            "saved_files": [cv_record["file_id"], avatar_record["file_id"]]
        }
    except Exception as e:
        # 5. Luồng Rollback nếu bất kỳ file nào lỗi
        process_rollback(temp_records)
        raise e

@router.get("/files")
def list_files():
    return {"total": len(file_metadata_db), "files": list(file_metadata_db.values())}

@router.get("/files/{file_id}")
def get_file_info(file_id: str):
    if file_id not in file_metadata_db:
        raise HTTPException(status_code=404, detail="File not found")
    return file_metadata_db[file_id]

@router.get("/files/{file_id}/download")
def download_file(file_id: str):
    if file_id not in file_metadata_db:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_metadata_db[file_id]
    file_path = Path(file_info["path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File physical path not found")
        
    return FileResponse(
        path=file_path, 
        filename=file_info["original_name"],
        media_type="application/octet-stream"
    )

@router.delete("/files/{file_id}")
def delete_file(file_id: str):
    if file_id not in file_metadata_db:
        raise HTTPException(status_code=404, detail="File not found")
        
    file_path = Path(file_metadata_db[file_id]["path"])
    if file_path.exists():
        file_path.unlink()
        
    del file_metadata_db[file_id]
    return {"success": True, "message": "File deleted successfully"}

@router.get("/storage/statistics")
def storage_stats():
    total_files = len(file_metadata_db)
    total_bytes = sum(f["size_bytes"] for f in file_metadata_db.values())
    total_mb = round(total_bytes / (1024 * 1024), 2)
    return {
        "total_files_stored": total_files,
        "total_storage_used_mb": total_mb
    }