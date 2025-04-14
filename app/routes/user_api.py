from fastapi import APIRouter, Depends, Body, HTTPException, status, Form, BackgroundTasks, Query
from sqlalchemy.orm import Session
from db.db_connection import get_db
import routes.user_logic as user_logic
from schemas import UserSignUpCreate, Token, UpdateUserBalance, UserPhotoSchema, UpdatePassword
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from datetime import timedelta
from pydantic import  EmailStr
from typing import Annotated
from fastapi.responses import FileResponse
 
router = APIRouter(prefix='/user', tags=['all the routes for the user'] )



# create account
@router.post('/sign_up')
async def route_for_sign_up(
    user_data:Annotated[UserSignUpCreate,Body()],
    background_tasks:BackgroundTasks,
    session:Session=Depends(get_db),
       )-> dict:
    try:
        user_data = await user_logic.sign_up(user_data,background_tasks,session)
        return user_data

    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")


# login 
@router.post('/sign_in')
async def get_access_token(
    form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
    session:Session=Depends(get_db))-> Token:
        unauthoriezed_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid username or password',
                            headers={"WWW-Authenticate": "Bearer"}) 
        user = user_logic.authenticate_user(form_data.username,form_data.password,session)

        if not user:
            raise unauthoriezed_exception
        token = user_logic.create_access_token(timedelta(minutes=30),data={'sub':user.username})     
        return {'access_token':token,'token_type':'bearer'}


# update user data
@router.patch('/update')
async def update_user_data(
    user_photo: UserPhotoSchema = Depends(),
    email: EmailStr = Form(...),
    address: str = Form(...),
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db)):
 
    try:
        user_data = user_logic.update_user_data(
            user_photo,
            email,
            address,
            user,
            session)
        return user_data

    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")


  


# update the balance
@router.patch('/update_balance')
async def route_for_updating_balance(
    amount:UpdateUserBalance,
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db),
       )-> dict:
    try:
        user_data = user_logic.update_balance(amount.balance,user,session)
        return user_data

    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")

 


# get current user data
@router.get('/user')
async def get_user(
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db),
       ):
    try:
        user_data = user_logic.get_user(user,session)
        return user_data

    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")


# remove account
@router.delete('/remove')
async def remove_user(
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db),
       ):
    try:
        user_data = user_logic.remove_user(user,session)
        return user_data

    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")


# update password

@router.patch('/update_password')
async def update_password(
    user_data:UpdatePassword,
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db)):
 
    try:
        user_data = user_logic.update_password(user_data,user,session)
        return user_data

    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")


  
# get file
@router.get('/img')
async def get_user(
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db),
    ):
    try:
        user_data = user_logic.get_file(user,session)
        return user_data

    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")
    
 