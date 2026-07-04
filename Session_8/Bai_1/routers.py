from fastapi import APIRouter, HTTPException, status
from typing import Optional
from schemas import CarrierCreate, CarrierUpdate, ShipmentCreate, CarrierStatus
from data import carriers, shipments

router = APIRouter()

@router.post("/carriers", status_code=status.HTTP_201_CREATED)
def create_carrier(carrier: CarrierCreate):
    for c in carriers:
        if c["code"] == carrier.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã code đã tồn tại"
            )
            
    new_id = max([c["id"] for c in carriers], default=0) + 1
    new_carrier = {
        "id": new_id,
        "code": carrier.code,
        "name": carrier.name,
        "max_weight_capacity": carrier.max_weight_capacity,
        "status": carrier.status.value
    }
    carriers.append(new_carrier)
    
    return {
        "message": "Thêm đối tác vận chuyển thành công",
        "data": new_carrier
    }

@router.get("/carriers")
def get_carriers(
    keyword: Optional[str] = None, 
    status: Optional[CarrierStatus] = None, 
    min_weight: Optional[int] = None
):
    result = carriers

    if keyword is not None:
        kw = keyword.lower()
        result = [
            c for c in result 
            if kw in c["code"].lower() or kw in c["name"].lower()
        ]

    if status is not None:
        result = [c for c in result if c["status"] == status.value]

    if min_weight is not None:
        result = [c for c in result if c["max_weight_capacity"] >= min_weight]

    return {
        "message": "Lấy danh sách đối tác vận chuyển thành công",
        "data": result
    }

@router.get("/carriers/{carrier_id}")
def get_carrier_detail(carrier_id: int):
    target = next((c for c in carriers if c["id"] == carrier_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Carrier not found"
        )
        
    return {
        "message": "Lấy chi tiết đối tác thành công",
        "data": target
    }

@router.put("/carriers/{carrier_id}")
def update_carrier(carrier_id: int, carrier_update: CarrierUpdate):
    target = next((c for c in carriers if c["id"] == carrier_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Carrier not found"
        )

    for c in carriers:
        if c["code"] == carrier_update.code and c["id"] != carrier_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã code đã tồn tại"
            )

    target["code"] = carrier_update.code
    target["name"] = carrier_update.name
    target["max_weight_capacity"] = carrier_update.max_weight_capacity
    target["status"] = carrier_update.status.value

    return {
        "message": "Cập nhật đối tác thành công",
        "data": target
    }

@router.delete("/carriers/{carrier_id}")
def delete_carrier(carrier_id: int):
    for index, c in enumerate(carriers):
        if c["id"] == carrier_id:
            deleted_carrier = carriers.pop(index)
            return {
                "message": "Xóa đối tác thành công",
                "data": deleted_carrier
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Carrier not found"
    )

@router.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(shipment: ShipmentCreate):
    carrier = next((c for c in carriers if c["id"] == shipment.carrier_id), None)
    
    if not carrier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Carrier not found"
        )
        
    if carrier["status"] != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Đối tác vận chuyển hiện không hoạt động"
        )
        
    if shipment.total_weight > carrier["max_weight_capacity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Khối lượng vượt quá năng lực vận chuyển tối đa của đối tác"
        )

    dispatch_str = shipment.dispatch_date.isoformat()
    
    for s in shipments:
        if s["carrier_id"] == shipment.carrier_id and s["dispatch_date"] == dispatch_str and s["shift"] == shipment.shift.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Đối tác vận chuyển đã được xếp lịch điều phối trong ca và ngày này"
            )

    new_id = max([s["id"] for s in shipments], default=0) + 1
    new_shipment = {
        "id": new_id,
        "carrier_id": shipment.carrier_id,
        "order_reference": shipment.order_reference,
        "total_weight": shipment.total_weight,
        "dispatch_date": dispatch_str,
        "shift": shipment.shift.value
    }
    shipments.append(new_shipment)
    
    return {
        "message": "Khởi tạo chuyến hàng thành công",
        "data": new_shipment
    }

@router.get("/shipments")
def get_shipments():
    return {
        "message": "Lấy danh sách các chuyến giao hàng thành công",
        "data": shipments
    }