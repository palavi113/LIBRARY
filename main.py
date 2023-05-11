from typing import Any
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from helpers.database import Base, engine, SessionLocal
from routers import users, books
from models import User, Book
from fastapi import FastAPI, HTTPException, status, Depends


from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()


Base.metadata.create_all(bind=engine)
# define secret key and algorithm
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# define username AND Password of admin
fake_users_db = {
    "pallavi": {
        "username": "pallavi",
        "full_name": "pallavi dobariya",
        "email": "pallavi@example.com",
        "hashed_password": "$2b$12$75TYwwkVzvbogIi60EIHRuYKLrj3b4e27K0Mza9eMbzFLtH2UYQCm",
        "disabled": False,
    }
}


# define schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify the password is correct or not"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password:str):
    """convert password in to hash password"""
    return pwd_context.hash(password)


def get_user(db: dict[str, Any], username: str):
    """check the user is available in dictionary"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    """ Authenticate User """
    user = get_user(fake_db, username)
    if not user:
        print('User not found...')
        return False

    if not verify_password(password, user.hashed_password):
        print('Password verification failed..')
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """get the current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    """find the user is available in dict or not"""
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password)
    print("User...")
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")

async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("users/display")
async def show(token: str = Depends(oauth2_scheme)):
    print(token)
    return "token created"
# app.include_router(authentication.router,tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["user"])
# app.include_router(books.router, prefix="/books", tags=["books"])
