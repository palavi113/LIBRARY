from helpers.database import SessionLocal
from models import User
from models.User import create_user,get_users
from fastapi import APIRouter

router = APIRouter()

# insert into user table
@router.post("")
async def create_user(name: str, email: str,password: str,role : str):
    return User.create_user(name,email,password,role)

# display from user table
@router.get("")
async def get_users():
    return User.get_users()
