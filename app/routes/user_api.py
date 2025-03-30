from fastapi import APIRouter, Depends , Body, HTTPException, status
from sqlalchemy.orm import Session
from db.db_connection import get_db
import routes.user_logic as user_logic
from schemas import UserSignUpCreate, Token
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from datetime import timedelta


router = APIRouter(prefix='/user', tags=['all the routes for the user'] )




@router.post('/sign_up')
async def route_for_sign_up(
    user_data:Annotated[UserSignUpCreate,Body()],
    session:Session=Depends(get_db) )-> dict:
    try:
        user_data = user_logic.sign_up(user_data,session)
        return user_data

    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")



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



  









@router.get('/secret')
async def the_secret(
    user:User=Depends(user_logic.get_current_user),
    session:Session=Depends(get_db)
      ):
    try:
        data = user_logic.get_user_data(user,session)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")








