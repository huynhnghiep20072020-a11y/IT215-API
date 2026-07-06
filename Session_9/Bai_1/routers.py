from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional, Tuple
from datetime import datetime, timezone
from schemas import TaskCreateSchema, TaskStatusUpdateSchema
from data import tasks_db

router = APIRouter()

def get_current_time_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def calculate_team_metrics() -> Tuple[int, int, float]:
    total_tasks = len(tasks_db)
    completed_tasks = sum(1 for task in tasks_db if task["status"] == "done")
    completion_rate_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    return total_tasks, completed_tasks, completion_rate_percentage

@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_all_tasks(request: Request, task_status: Optional[str] = None):
    result = tasks_db
    if task_status is not None:
        result = [t for t in result if t["status"] == task_status]
        
    return {
        "statusCode": status.HTTP_200_OK,
        "message": "Lấy danh sách công việc thành công!",
        "data": result,
        "error": None,
        "timestamp": get_current_time_str(),
        "path": request.url.path
    }

@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreateSchema, request: Request):
    for t in tasks_db:
        if t["title"] == task_in.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Lỗi: Tiêu đề công việc này đã tồn tại trong nhóm!",
                    "error": "ERR-TASK-01: Task conflict: Title field duplicates an existing record."
                }
            )
            
    new_id = max([t["id"] for t in tasks_db], default=0) + 1
    new_task = {
        "id": new_id,
        "title": task_in.title,
        "description": task_in.description,
        "assignee": task_in.assignee,
        "priority": task_in.priority,
        "status": "todo",
        "created_at": get_current_time_str()
    }
    
    tasks_db.append(new_task)
    
    return {
        "statusCode": status.HTTP_201_CREATED,
        "message": "Khởi tạo công việc mới thành công!",
        "data": new_task,
        "error": None,
        "timestamp": get_current_time_str(),
        "path": request.url.path
    }

@router.get("/tasks/analytics/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_analytics(request: Request):
    total_tasks, completed_tasks, completion_rate_percentage = calculate_team_metrics()
    
    return {
        "statusCode": status.HTTP_200_OK,
        "message": "Lấy số liệu thống kê hiệu suất nhóm thành công!",
        "data": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate_percentage": completion_rate_percentage
        },
        "error": None,
        "timestamp": get_current_time_str(),
        "path": request.url.path
    }

@router.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def update_task_status(task_id: int, status_in: TaskStatusUpdateSchema, request: Request):
    target_task = next((t for t in tasks_db if t["id"] == task_id), None)
    
    if not target_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Lỗi: Không tìm thấy công việc yêu cầu!",
                "error": "ERR-TASK-03: Task not found in the system."
            }
        )
        
    if target_task["status"] == "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi: Không thể lùi trạng thái của công việc đã hoàn thành!",
                "error": "ERR-TASK-04: Cannot update or reverse a task that is already marked as done."
            }
        )
        
    target_task["status"] = status_in.status
    
    return {
        "statusCode": status.HTTP_200_OK,
        "message": "Cập nhật tiến độ công việc thành công!",
        "data": target_task,
        "error": None,
        "timestamp": get_current_time_str(),
        "path": request.url.path
    }