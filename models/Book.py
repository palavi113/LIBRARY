from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from helpers.database import Base,engine,SessionLocal
from pydantic import BaseModel
# create table

class Book(Base):

    __tablename__ = "books"

    book_id = Column(Integer,unique = True,primary_key = True)
    book_name  = Column(String,index = True,unique = True)
    is_available = Column(Boolean,default = True)

Base.metadata.create_all(bind=engine)

def create_book(book_name : str):
    db = SessionLocal()
    book = Book(book_name = book_name)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def get_books():
    db = SessionLocal()
    books = db.query(Book).all()
    return books

def get_book(id : int):
    db = SessionLocal()
    book1 = db.query(Book).filter(Book.book_id ==id).first()
    return book1

def update_book(book_nm:str,id : int):
    print("hello")
    db = SessionLocal()
    book = db.query(Book).filter(Book.book_id ==id)
    book.book_name =book_nm
    db.commit()

