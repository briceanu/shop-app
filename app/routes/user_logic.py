from sqlalchemy.orm import Session
from schemas import UserSignUpCreate, UserPhotoSchema, UpdatePassword
from passlib.context import CryptContext
from sqlalchemy import insert, select, update, delete
from models import User
import jwt
from datetime import timedelta, datetime, timezone
from config import settings
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status, status
from typing import Annotated
import os , shutil
from pydantic import EmailStr
from decimal import Decimal
from fastapi import BackgroundTasks
from routes.send_email import send_in_background
from fastapi.responses import FileResponse
import uuid

from redis_client import redis_client


SECRET = settings.SECRET
ALGORITHM = settings.ALGORITHM
REFRESH_SECRET = settings.REFRESH_SECRET
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/sign_in')


async def sign_up(user_data:UserSignUpCreate,
            background_tasks: BackgroundTasks,
            session:Session):
    stmt = insert(User).values(
        username=user_data.username,
        password=pwd_context.hash(user_data.password),
        email=user_data.email)    
    session.execute(stmt) 
    session.commit()
    
    # send a mail using the background task
    await send_in_background([user_data.email],
                       background_tasks,
                       username=user_data.username,
                       )
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


def create_refresh_token(expires_delta:timedelta,data:dict):
    to_encode=data.copy()
    expires= datetime.now(timezone.utc) + expires_delta
    jti=str(uuid.uuid4())
    to_encode.update({'exp':expires,'jti':jti})
    refresh_token = jwt.encode(to_encode,REFRESH_SECRET ,algorithm=ALGORITHM)
    return refresh_token


def blacklist_token(jti: str, ttl: int):
    redis_client.setex(f"blacklist:{jti}", ttl, "true")

# ttl = time to live
def is_token_blacklisted(jti: str) -> bool:
    return redis_client.exists(f"blacklist:{jti}") == 1


def logout(token:str):
    try:
        payload = jwt.decode(token,REFRESH_SECRET,algorithms=ALGORITHM)
        jti = payload.get('jti')
        exp = payload.get('exp')

        if not jti or not exp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid token')
        if redis_client.exists(f'blacklist:{jti}')==1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Token already blacklisted')
 
        ttl = exp - int(datetime.now(timezone.utc).timestamp())
        blacklist_token(jti,ttl)
        return {"success":'Logged out successfully'}
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")




def return_access_from_refresh(token:str,session:Session):
    try:
        payload = jwt.decode(token,REFRESH_SECRET, algorithms=ALGORITHM)
        jti = payload.get('jti')
        username = payload.get('sub')
        username_from_db = session.execute(select(User.username).where(User.username==username)).scalar()

        if not jti or not username_from_db:
            raise HTTPException(status_code=401, detail="Invalid token")

        if is_token_blacklisted(jti):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        access_token = create_access_token(timedelta(minutes=30),data={'sub':username_from_db})
        return access_token
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# get the current user from token
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


def update_user_data(
        user_data:UserPhotoSchema,
        email:EmailStr,
        address:str,
        user:User,
        session:Session):
    
# in a production environment we save the images on a S3 bucket
    DIR = 'uploads/'
    IMG_DIR = os.path.join(DIR, user)  

    os.makedirs(IMG_DIR, exist_ok=True)
    file_path = os.path.join(IMG_DIR, user_data.user_photo.filename)  

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(user_data.user_photo.file, buffer)

    stmt = update(User).where(User.username==user).values(
        user_photo=file_path,
        email=email,
        address=address
        )
    result = session.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this blog")
    session.commit()
    return {'success':'your data has been updated'}
 


def update_balance(amount:Decimal,
                   user:User,
                   session:Session):
    stmt = update(User).where(User.username==user).values(balance=amount)
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorized to perform this action')
    session.commit()
    return {'success':'balance updated'}




def get_user(user_data:User,session:Session):
    stmt = select(User).where(User.username==user_data)
    user = session.execute(stmt).scalar_one_or_none()

        # 
    """here we get the user with its products and images"""
    # stmt = (select(User)
    #         .options(joinedload(User.products).joinedload(Product.images))
    #         .where(User.username==user_data))
    # user = session.execute(stmt).unique().scalars().all()

        # 
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'no user with the username {user_data} found.')
    return user





def remove_user(user_data:User,session:Session):
    stmt = delete(User).where(User.username==user_data)
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'no user with the username {user_data} found.')

    session.commit()
    return {'success':'your account has been removed'}




def update_password(user_data:UpdatePassword,
                    user:User,
                    session:Session):
     
    stmt = ( update(User)
            .where(User.username == user)
            .values(password=pwd_context.hash( user_data.new_password)))

    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'no user with the username {user} found.')

    session.commit()
    return {'success':'password updated'}


# get user profile image
def get_file(user:User,
             session:Session,
             ):
        stmt = select(User.user_photo).where(User.username==user)
        file_path = session.execute(stmt).scalar() 
        if not file_path:
            raise HTTPException(status_code=404, detail="Profile image not found")
    
        return FileResponse(file_path)

 