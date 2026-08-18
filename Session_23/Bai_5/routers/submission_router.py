from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import SubmissionCreate, GradeUpdate
from dependencies.auth_deps import get_current_user, require_admin
from models.mock_db import submissions_db, assignments_db, counters

router = APIRouter(tags=["Submissions"])

@router.post("/submissions", status_code=201)
def submit_assignment(sub: SubmissionCreate, current_user: dict = Depends(get_current_user)):
    if sub.assignment_id not in assignments_db:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    counters["submission"] += 1
    new_id = counters["submission"]
    new_sub = {
        "id": new_id, 
        "assignment_id": sub.assignment_id, 
        "user_id": current_user["id"], 
        "url": sub.content_url,
        "score": None
    }
    submissions_db[new_id] = new_sub
    return new_sub

# ENDPOINT DÀNH RIÊNG CHO ADMIN (2)
@router.get("/submissions")
def get_all_submissions(admin_user: dict = Depends(require_admin)):
    return list(submissions_db.values())

# KIỂM TRA QUYỀN SỞ HỮU DỮ LIỆU (IDOR CHECK)
@router.get("/users/{user_id}/submissions")
def get_user_submissions(user_id: str, current_user: dict = Depends(get_current_user)):
    # User thông thường truy cập dữ liệu người khác -> 403
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view other user's data")
        
    return [s for s in submissions_db.values() if s["user_id"] == user_id]

# ENDPOINT DÀNH RIÊNG CHO ADMIN (3)
@router.patch("/submissions/{sub_id}/grade")
def grade_submission(sub_id: int, grade: GradeUpdate, admin_user: dict = Depends(require_admin)):
    submission = submissions_db.get(sub_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    submission["score"] = grade.score
    return {"message": "Graded successfully", "data": submission}