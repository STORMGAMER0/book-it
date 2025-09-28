import os
from uuid import UUID

from dotenv import load_dotenv
from fastapi import Depends, HTTPException,status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime,timedelta,timezone
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session


from models import User

security = HTTPBearer()

load_dotenv()

JWT_SECRET_KEY =os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM =os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str)-> bool:
    return pwd_context.verify(plain_password, hashed_password)


#JWT TOKEN SECTION

def create_access_token(data:dict, expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp":expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode,JWT_SECRET_KEY,JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access")->Optional[dict]:
    #this function is to verify and decode jwt token
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, JWT_ALGORITHM)

        if payload.get("type") != token_type:
            return None

        expiry = payload.get("exp")
        if expiry is None:
            return None

        if datetime.fromtimestamp(expiry, tz=timezone.utc) < datetime.now(timezone.utc):
            return None

        return payload

    except JWTError:
        None
from core.database import get_db

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db : Session = Depends(get_db)):
    print("GET_CURRENT_USER CALLED!")  # This should print if dependency runs
    print(f"Credentials: {credentials}")
    from crud.user import UserCRUD

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)

    try:
        token = credentials.credentials

        payload = verify_token(token, token_type="access")
        if payload is None:
            raise credentials_exception

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = UserCRUD.get_user_by_id(db,user_id)
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)):
    from crud.user import UserCRUD
    """Require admin role for protected routes"""
    if not UserCRUD.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user