from fastapi import APIRouter

router = APIRouter()

@router.get("/products")
def get_all_products():
    return {
        "message": "Lấy danh sách sản phẩm thành công",
        "data": []
    }

@router.get("/products/detail")
def get_product_detail():
    return {
        "message": "Lấy chi tiết sản phẩm thành công",
        "data": {}
    }

@router.post("/products")
def create_product():
    return {
        "message": "Thêm sản phẩm mới thành công"
    }

@router.put("/products/update")
def update_product():
    return {
        "message": "Cập nhật thông tin sản phẩm thành công"
    }

@router.delete("/products/delete")
def delete_product():
    return {
        "message": "Xóa sản phẩm thành công"
    }

@router.get("/products/statistics")
def get_product_statistics():
    return {
        "message": "Lấy thống kê sản phẩm thành công",
        "data": {"total_products": 100, "active_products": 80}
    }

@router.get("/products/bestsellers")
def get_bestselling_products():
    return {
        "message": "Lấy danh sách sản phẩm bán chạy thành công",
        "data": []
    }

@router.get("/products/out-of-stock")
def get_out_of_stock_products():
    return {
        "message": "Lấy danh sách sản phẩm hết hàng thành công",
        "data": []
    }