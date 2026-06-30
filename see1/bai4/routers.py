from fastapi import APIRouter
from data import books

router = APIRouter()

@router.get("/books/low-stock")
def get_low_stock_books():
    low_stock_books = []
    
    for book in books:
        if "quantity" not in book:
            continue
            
        quantity = book["quantity"]
        
        if quantity < 0:
            continue
            
        if quantity <= 5:
            low_stock_books.append(book)
            
    if not low_stock_books:
        return {
            "message": "Không có sách nào sắp hết hàng",
            "data": []
        }
        
    return {
        "message": "Danh sách sách sắp hết hàng",
        "data": low_stock_books
    }