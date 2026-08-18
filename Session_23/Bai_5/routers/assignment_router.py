from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import AssignmentCreate
from dependencies.auth_deps import get_current_user, require_admin
from models.mock_db import assignments_db, counters

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.get("/")
def get_all_assignments(current_user: dict = Depends(get_current_user)):
    return list(assignments_db.values())

# ENDPOINT DÀNH RIÊNG CHO ADMIN (1)
@router.post("/", status_code=201)
def create_assignment(assignment: AssignmentCreate, admin_user: dict = Depends(require_admin)):
    counters["assignment"] += 1
    new_id = counters["assignment"]
    new_item = {"id": new_id, "title": assignment.title, "description": assignment.description}
    assignments_db[new_id] = new_item
    return new_item