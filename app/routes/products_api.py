from fastapi import APIRouter, HTTPException,status, Depends, Body, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from schemas import ProductSchemaCreate, ProductImageCreate, Products, OrderItemSchema, OrderResponse
from . import products_logic 
from . import user_logic
from models import User
from typing import Annotated, List
from db.db_connection import get_db
import uuid
from pydantic import PositiveInt



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
        result = products_logic.remove_product(product_id,session,user)
        return result
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500,
                        detail=f"An error occurred: {str(e)}")




@router.post('/place_order')
async def place_order(
    products:OrderItemSchema,
    session:Session=Depends(get_db),
    user:User=Depends(user_logic.get_current_user),
    ):
    try:
        products= products_logic.place_order(products,session,user)
        return products

    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'an error occured :{e.orig}')
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500,
                        detail=f"An error occurred: {str(e)}")


@router.get('/show_orders', response_model=List[OrderResponse])
async def show_all_orders(
    session:Session=Depends(get_db)):
    try:
        orders = products_logic.show_all_orders(session)
        return orders
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500,
                        detail=f"An error occurred: {str(e)}")






# filtering the products

@router.get('/')
async def filter_products(min_price:float,max_price:float,
                          session:Session=Depends(get_db)):
    
            try:
                products = products_logic.filter_products(min_price,max_price,session)
                return products
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")


# count all the products

@router.get('/all')
async def  count_all_products(session:Session=Depends(get_db)):
    
            try:
                products = products_logic.count_products(session)
                return products
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")

# all products greater than int

@router.get('/gt')
async def  count_all_products_gt_int(price:Annotated[PositiveInt,Query()],
                                     session:Session=Depends(get_db)):
    
            try:
                products = products_logic.count_products_gt(price,session)
                return products
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
            
# label the products

@router.get('/label')
async def  label_products(session:Session=Depends(get_db)):
    
            try:
                products = products_logic.label_products(session)
                return products
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
            

@router.get('/expelsive')
async def  expensive_product(session:Session=Depends(get_db)):
    
            try:
                product = products_logic.expensive_product(session)
                return product
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
            

@router.get('/users_without_photo')
async def  users_photo(session:Session=Depends(get_db))->dict:
    
            try:
                product = products_logic.select_users(session)
                return product
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
            
@router.get('/select_data')
async def  select_data(session:Session=Depends(get_db)):
    
            try:
                product = products_logic.select_data(session)
                return product
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
            



# hacked route



@router.get('/hack')
async def filter_products(min_price:str,
                          session:Session=Depends(get_db)):
    
            try:
                products = products_logic.hack_products(min_price,session)
                return products
            except HTTPException:
                raise 
            except Exception as e:
                raise HTTPException(status_code=500,
                                detail=f"An error occurred: {str(e)}")
