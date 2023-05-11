from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Hash:
    def bcrypt(self,password : str):
        hash_pass = pwd_context.hash(password)
        return hash_pass
    
    def verify(self,plain_password : str,hashed_password : str):
        return pwd_context.verify(plain_password,hashed_password)
