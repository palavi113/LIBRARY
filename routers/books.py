from helpers.database import SessionLocal
from models import Book
from models.Book import create_book,get_books,get_book
from fastapi import APIRouter
router = APIRouter()

# Insert into book table
@router.post("/")
async def create_book(book_name : str):
    return Book.create_book(book_name)
    
# Display from book table
@router.get("/")
async def get_books():
    return Book.get_books()

@router.get("/{book_id}")
async def issue_book(book_id):
    return Book.get_book(book_id)

@router.put("/update")
async def update_book(book_nm : str,id : int):
    return Book.update_book(book_nm,id)