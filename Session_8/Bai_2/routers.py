from fastapi import APIRouter, HTTPException, status
from typing import Optional
from schemas import AssetCreate, AssetUpdate, AllocationCreate, AssetStatus
from data import assets, allocations

router = APIRouter()

@router.post("/assets", status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetCreate):
    for a in assets:
        if a["serial_number"] == asset.serial_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã serial_number đã tồn tại trong hệ thống"
            )
            
    new_id = max([a["id"] for a in assets], default=0) + 1
    new_asset = {
        "id": new_id,
        "serial_number": asset.serial_number,
        "model": asset.model,
        "stock_available": asset.stock_available,
        "status": asset.status.value
    }
    assets.append(new_asset)
    
    return {
        "message": "Khai báo tài sản thiết bị thành công",
        "data": new_asset
    }

@router.get("/assets")
def get_assets(
    keyword: Optional[str] = None,
    status: Optional[AssetStatus] = None,
    min_stock: Optional[int] = None
):
    result = assets

    if keyword is not None:
        kw = keyword.lower()
        result = [
            a for a in result
            if kw in a["serial_number"].lower() or kw in a["model"].lower()
        ]

    if status is not None:
        result = [a for a in result if a["status"] == status.value]

    if min_stock is not None:
        result = [a for a in result if a["stock_available"] >= min_stock]

    return {
        "message": "Lấy danh mục tài sản thành công",
        "data": result
    }

@router.get("/assets/{asset_id}")
def get_asset_detail(asset_id: int):
    target = next((a for a in assets if a["id"] == asset_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
        
    return {
        "message": "Lấy thông tin chi tiết tài sản thành công",
        "data": target
    }

@router.put("/assets/{asset_id}")
def update_asset(asset_id: int, asset_update: AssetUpdate):
    target = next((a for a in assets if a["id"] == asset_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    for a in assets:
        if a["serial_number"] == asset_update.serial_number and a["id"] != asset_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã serial_number đã tồn tại trong hệ thống"
            )

    target["serial_number"] = asset_update.serial_number
    target["model"] = asset_update.model
    target["stock_available"] = asset_update.stock_available
    target["status"] = asset_update.status.value

    return {
        "message": "Cập nhật thông tin tài sản thành công",
        "data": target
    }

@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: int):
    for index, a in enumerate(assets):
        if a["id"] == asset_id:
            deleted_asset = assets.pop(index)
            return {
                "message": "Xóa tài sản thiết bị thành công",
                "data": deleted_asset
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Asset not found"
    )

@router.post("/allocations", status_code=status.HTTP_201_CREATED)
def create_allocation(allocation: AllocationCreate):
    asset = next((a for a in assets if a["id"] == allocation.asset_id), None)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài sản thiết bị không tồn tại"
        )
        
    if asset["status"] != "READY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiết bị không ở trạng thái sẵn sàng (READY) để bàn giao"
        )
        
    if allocation.allocated_quantity > asset["stock_available"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng cấp phát vượt quá số lượng tồn kho khả dụng"
        )

    asset["stock_available"] -= allocation.allocated_quantity

    new_id = max([al["id"] for al in allocations], default=0) + 1
    new_allocation = {
        "id": new_id,
        "asset_id": allocation.asset_id,
        "employee_email": allocation.employee_email,
        "allocated_quantity": allocation.allocated_quantity,
        "start_date": allocation.start_date.isoformat(),
        "duration_months": allocation.duration_months
    }
    
    allocations.append(new_allocation)
    
    return {
        "message": "Đăng ký cấp phát thiết bị thành công",
        "data": new_allocation
    }

@router.get("/allocations")
def get_allocations():
    return {
        "message": "Lấy danh sách lịch sử cấp phát thành công",
        "data": allocations
    }