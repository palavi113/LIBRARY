
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from helpers import database
from helpers.database import Base,SessionLocal,engine
from pydantic import BaseModel
import hashing
# create tabl


class User(Base):
    __tablename__ = "USER"

    user_id = Column(Integer, primary_key=True, index=True)
    Name = Column(String,index = True)
    Email = Column(String, unique=True, index=True)
    Hashed_password = Column(String)
    role = Column(String)


class admin(BaseModel):
    username : str
    password : str


Base.metadata.create_all(bind=engine)


def create_user(name: str, email: str,password: str,role : str):
    db = SessionLocal()
    user = User(Name=name, Email=email,Hashed_password = hashing.Hash.bcrypt(password),role = role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    return users




