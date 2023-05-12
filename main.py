from typing import Any
from jose import jwt
from fastapi import Depends, FastAPI, HTTPException, status,Path
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import create_engine
from datetime import datetime, timedelta,date
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# custom
from hashing import Hash as sh
<<<<<<< HEAD

=======
>>>>>>> eeeead5 (No change)
app = FastAPI()

# define secret key and algorithm
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# create connection with database
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create user class
class User(Base):

    __tablename__ = "USER"

    user_id = Column(Integer, primary_key=True, index=True)
    Name = Column(String,index = True)
    Email = Column(String, unique=True, index=True)
    Hashed_password = Column(String)
    role = Column(String)

class Book_lib(Base):
    
    __tablename__ = "book_library"

    book_id = Column(Integer,primary_key=True,index=True)
    book_name = Column(String,index=True)
    book_price = Column(Integer,index=True)
    is_available = Column(Boolean,default=True)

class Book_Issue(Base):

    __tablename__ = "book_issue"

    issue_id = Column(Integer,primary_key=True)
    book_name = Column(String)
    user_name = Column(String)
    issue_date = Column(String)
    return_date = Column(String)

# create all tables
Base.metadata.create_all(bind=engine)

# define token schema
class Token:
    access_token: str
    token_type: str

def get_user(user :User,user_nm : str):
    """authenticate the user is valid or not"""
    usr_nm = session.query(User).filter(User.Name == user_nm).first()
    print(usr_nm.Name)
    if usr_nm.Name == user_nm:
        return usr_nm.Name
    return False
 
def get_role(user :User,user_role : str,usr_name : str):
    """authenticate the user role is valid or not"""
    print("in get_role method print role : ",user_role)
    usr_role = session.query(User).filter(User.Name == usr_name).first()
    if usr_role.role =='admin':
        return user_role

def authenticate_user(userdb : User, username: str, password: str):
    """ Authenticate User """
    db = SessionLocal()
    usr = db.query(User).filter(User.Name == username).first()
    
    # check the user is available in table
    user = get_user(userdb,username)
    if not user:
        return False
    
    # check the user role is correct or not
    usr_role = get_role(userdb,usr.role,username)
    if not usr_role:
        return False
    
    if not sh.verify(password, usr.Hashed_password):
        return False
    return True

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# authorize user and generate token
@app.post("/token",tags=['Authentication'])
async def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(User,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub" : form_data.username},
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# create user
@app.post("/create_user",tags=['Users'])
async def create_user(name: str, email: str,password: str,role : str,token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    user = User(Name=name, Email=email,Hashed_password = sh.bcrypt(password),role = role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# display all users
@app.get("/",tags=['Users'])
async def get_users(token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    users = db.query(User).all()
    return users

# update user details
@app.put("/{id}",tags=['Users'])
async def update_user(id : int,name : str,email : str,token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == id).first()
    user.Name = name
    user.Email = email
    db.commit()
    return user

# delete user 
@app.delete("/{nm}",tags=['Users'])
async def del_user(name : str= Path(...),token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    user = db.query(User).filter(User.Name == name).delete()
    db.commit()
    db.refresh(user)
    return user

# create book
@app.post("/create_book",tags=['Books'])
async def create_book(book_id : int,book_nm : str,book_price : int,is_avl : bool,token: str = Depends(oauth2_scheme)):
    print(book_id)
    db = SessionLocal()
    book = Book_lib(book_id = book_id,book_name = book_nm,book_price = book_price,is_available = is_avl)
    db.add(book)
    db.commit()
    db.refresh(Book_lib)
    return book

# display all books
@app.get("/display",tags=['Books'])
async def get_books():
    db = SessionLocal()
    books1 = db.query(Book_lib).all()
    return books1

# display and specific books details
@app.get("/{nm}",tags=["Books"])
async def get_book(book_nm : str = Path(...),token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    book = db.query(Book_lib).filter(Book_lib.book_name == book_nm).first()
    return book

# update the book details
@app.put("/",tags=["Books"])
async def update_book(book_id : int,book_nm : str,book_prc : int,token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    book_updt = db.query(Book_lib).filter(Book_lib.book_id == book_id).first()
    book_updt.book_name =  book_nm
    book_updt.book_price = book_prc
    db.commit()
    db.refresh(Book_lib)

# delete book from table
@app.delete("/",tags=["Books"])
async def delete_book(book_id : int,token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    book_del = db.query(Book_lib).filter(Book_lib.book_id == book_id).delete()
    db.commit()
    db.refresh

# issue the books
# @app.get("/issue_book",tags=["Issue"])
@app.post("/issue",tags=["Issue"])
async def issue_book_user(book_nm : str, user_nm :str,token: str = Depends(oauth2_scheme)):
    print("hello")
    db = SessionLocal()
    book = db.query(Book_lib).filter(Book_lib.book_name == book_nm).first()
    if book:
        print(book.book_id)
        print(book.book_name)
        print(book.is_available)
    usr  = db.query(User).filter(User.Name == user_nm).first()
    """check the book is availble or not"""
    if book.is_available == True:
        print("book is available")
        """check the user is available or not"""
        if usr:
            print("user is valid")
            """change the book avilable status"""
            book.is_available = False
            db.commit()

            """insert details in issue table"""
            isue_date = date.today().strftime("%d/%m/%Y")
            retun_date = (date.today() + timedelta(days=15)).strftime("%d/%m/%Y")

            db = SessionLocal()
            isu_book = Book_Issue(book_name = book_nm,user_name = user_nm,issue_date = isue_date,return_date = retun_date)
            db.add(isu_book)
            db.commit()
            if isu_book:
                return "Record Inserted"
            return "Record Not Inserted"
        return "User Not Found"
    return "Book Is Not Available"

@app.post("/return",tags=["Return"])
async def return_book_user(book_nm : str, user_nm :str,token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    book = db.query(Book_lib).filter(Book_lib.book_name == book_nm).first()
    if book:
        print(book.book_id)
        print(book.book_name)
        print(book.is_available)
    usr  = db.query(User).filter(User.Name == user_nm).first()
    """check the book is availble or not"""
    if book.is_available == False:
        """check the user is available or not"""
        if usr:
            print("user is valid")
            """change the book avilable status"""
            book.is_available = True
            db.commit()
            return " Thank you"
        return "User Not Found"        
    return "Book Is already returned"
