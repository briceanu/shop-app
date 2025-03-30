from sqlalchemy.orm import Session
from schemas import UserSignUpCreate
from passlib.context import CryptContext
from sqlalchemy import insert, select
from models import User
import jwt
from datetime import timedelta, datetime, timezone
from config import settings
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from typing import Annotated



SECRET = settings.SECRET
ALGORITHM = settings.ALGORITHM
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/sign_in')


def sign_up(user_data:UserSignUpCreate,session:Session):
    stmt = insert(User).values(
        username=user_data.username,
        password=pwd_context.hash(user_data.password))

    session.execute(stmt) 
    session.commit()
    # send a mail using the background task
    return {'success':'your account has been created'}


def authenticate_user(username:str,password:str,session:Session):
    stmt = select(User).where(User.username==username)
    user = session.execute(stmt).scalar()
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


def create_access_token(expires_delta:timedelta,data:dict):
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp':expires})
    token = jwt.encode(to_encode,SECRET,algorithm=ALGORITHM)
    return token
 

 



def get_current_user( 
                    token:Annotated[str,Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token,SECRET, algorithms=ALGORITHM)
        user = payload.get('sub')
        if not user:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return user



def get_user_data(user:User,session:Session):
    stmt = select(User).where(User.username==user)
    user = session.execute(stmt).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'no user with the username {user} found.')
    return user