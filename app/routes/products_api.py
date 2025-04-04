from fastapi import APIRouter, HTTPException,status, Depends, Body, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from schemas import ProductSchemaCreate, ProductImageCreate
from . import products_logic 
from . import user_logic
from models import User
from typing import Annotated
from db.db_connection import get_db
import uuid



router = APIRouter(prefix='/products',tags=['the urls for the products'])


@router.post('/upload_product')
async def upload_product(
    data:Annotated[ProductSchemaCreate,Body()],
    session:Session=Depends(get_db),
    user:User=Depends(user_logic.get_current_user),
    )-> dict:
    try:
        product= products_logic.upload_product(data,session,user)
        return product
    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")

# list all products


@router.get('/list_products')
async def list_products(
    session:Session=Depends(get_db),
    user:User=Depends(user_logic.get_current_user),
    ):
    try:
        product= products_logic.list_products(session,user)
        return product
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")






@router.patch('/upload_image')
async def upload_image(
    data:ProductImageCreate=Depends(),
    session:Session=Depends(get_db),
    user:User=Depends(user_logic.get_current_user),
    )-> dict:
    try:
        product= products_logic.image_upload(data,session,user)
        return product
    except HTTPException:
        raise 
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'error: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred: {str(e)}")

 
@router.delete('/remove')
async def remove_product(
                        product_id:Annotated[uuid.UUID,Query()],
                        session:Session=Depends(get_db),
                        user:User=Depends(user_logic.get_current_user),
                        ):
    try:
        result = products_logic.remove_product(session,user,product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500,
                        detail=f"An error occurred: {str(e)}")

