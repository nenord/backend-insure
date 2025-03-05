from fastapi import Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from passlib.context import CryptContext # type: ignore
from pymongo import MongoClient # type: ignore
from datetime import datetime, timedelta, timezone
from dotenv import dotenv_values
from typing import Optional
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from models import User_Out

config = dotenv_values(".env")
SECRET_KEY = config["SECRET_KEY"]
ALGORITHM = "HS256"
EXPIRE_TOKEN = config["EXPIRE_TOKEN"]

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(EXPIRE_TOKEN))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def find_user_email(email: str, app):
    if (user := app["users"].find_one({"email": email})) is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")

def find_user_id(id: str):
    mongo_client = MongoClient(config["ATLAS_URI"])
    mongo_db = mongo_client[config["DB_NAME"]]
    if (user := mongo_db["users"].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_id: str = payload.get("sub")
        if token_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = find_user_id(token_id)
    if user is None:
        raise credentials_exception
    return User_Out(**user)