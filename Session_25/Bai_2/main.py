# Phần 1. Phát hiện lỗi
# Dưới đây là các lỗ hổng nghiêm trọng trong đoạn code hiện tại:

# Cách lấy phần mở rộng file sai lệch (Gây lỗi bảo mật và crash):

# Đoạn code extension = document.filename.split(".")[1] rất nguy hiểm. Nếu file tên là baitap.pdf.exe, nó sẽ lấy phần tử thứ 1 là pdf để đưa qua vòng kiểm duyệt, dẫn đến việc hacker upload thành công file thực thi .exe.

# Nếu file không có phần mở rộng (ví dụ: README), code sẽ bị crash ngay lập tức với lỗi IndexError vì không có phần tử thứ 1 sau khi split(".").

# Không tự động tạo thư mục lưu trữ: Code sử dụng thẳng UPLOAD_FOLDER nhưng không có lệnh khởi tạo. Điều này dẫn đến lỗi FileNotFoundError làm crash API nếu thư mục storage/documents chưa tồn tại trên server.

# Nguy cơ ghi đè file và sử dụng tên file không an toàn: Code hiện tại dùng nguyên document.filename do người dùng gửi lên để làm tên lưu trên server. Nếu hai người cùng upload file tên bai-tap.pdf, file trước sẽ bị ghi đè. Ngoài ra, hacker có thể gửi tên file chứa ký tự điều hướng (../../../) để thực hiện tấn công Path Traversal.

# Không kiểm tra file rỗng và dung lượng file: Code hiện tại bỏ qua việc kiểm tra độ lớn file. Người dùng có thể upload file rỗng (0 byte) tạo ra dữ liệu rác, hoặc upload file khổng lồ (vài GB) gây tràn bộ nhớ (Out of Memory) do lệnh await document.read() đọc toàn bộ dữ liệu vào RAM.

# Không chuẩn hóa mã môn học và thiếu kiểm tra loại tài liệu:

# Mã môn học không được sử dụng .upper() để chuẩn hóa, dẫn đến dữ liệu lưu trữ bị phân mảnh (ví dụ: it215 và IT215).

# Biến document_type và title cũng không được kiểm tra (chống rỗng, hoặc so khớp danh sách lecture, assignment, reference).

import uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status

app = FastAPI()

# Định nghĩa thư mục bằng Pathlib
UPLOAD_FOLDER = Path("storage/documents")

# Tạo thư mục tự động nếu chưa tồn tại
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Các cấu hình kiểm tra
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
ALLOWED_DOCUMENT_TYPES = {"lecture", "assignment", "reference"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/documents")
async def upload_document(
    title: str = Form(...),
    course_code: str = Form(...),
    document_type: str = Form(...),
    description: str = Form(""),
    document: UploadFile = File(...),
):
    # 1. Kiểm tra tiêu đề không được rỗng
    if not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    # 2. Kiểm tra loại tài liệu
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type"
        )

    # 3. Chuẩn hóa mã môn học (Viết hoa)
    normalized_course_code = course_code.strip().upper()

    # 4. Lấy và kiểm tra phần mở rộng file an toàn
    # Path.suffix lấy phần mở rộng cuối cùng (vd: baitap.pdf.exe -> .exe)
    extension = Path(document.filename).suffix.lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{extension}' is not allowed"
        )

    # Đọc dữ liệu file
    content = await document.read()
    file_size = len(content)

    # 5. Kiểm tra file rỗng và file vượt quá dung lượng
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File cannot be empty"
        )
        
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10MB limit"
        )

    # 6. Tạo tên file duy nhất chống ghi đè
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_FOLDER / unique_filename

    # Lưu file
    with open(file_path, "wb") as output_file:
        output_file.write(content)

    return {
        "success": True,
        "message": "Document uploaded successfully",
        "data": {
            "title": title.strip(),
            "course_code": normalized_course_code,
            "document_type": document_type,
            "description": description.strip(),
            "original_filename": document.filename,
            "saved_filename": unique_filename,
            "file_path": str(file_path),
        },
    }