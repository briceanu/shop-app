from pydantic import (Field,
                      BaseModel,
                      Field, 
                      field_validator,
                      model_validator,
                      EmailStr)
import re
from typing import Annotated, List
from decimal import Decimal
from fastapi import UploadFile, HTTPException, status
# import uuid
from uuid import UUID




 

def validate(value):
    if len(value) < 6:
        raise ValueError('Password must be at least 6 characters long')
    if not re.search(r'[A-Za-z]', value):  # Check for at least one letter
        raise ValueError('Password must include at least one letter')
    if not re.search(r'\d', value): 
        raise ValueError('Password must contain at least one number')
    
    return value
     





class UserSignUpCreate(BaseModel):
    username:str = Field(...,max_length=60)
    password:str
    confirm_password: str
    email:EmailStr 
    class Config:
        extra = 'forbid'


    @field_validator('password')
    @classmethod
    def validate_password(cls,value):
        return validate(value)
    
    @model_validator(mode='before')
    @classmethod
    def validate(cls,values):
        if values.get('password') != values.get('confirm_password'):
            raise ValueError('Passwords do not match')
        return values


class Token(BaseModel):
    access_token:str
    token_type:str


# the validation for the balance
BalanceType = Annotated[Decimal, Field(gt=0, max_digits=7, decimal_places=2)]
class UpdateUserBalance(BaseModel):
    balance: BalanceType
  
class UserPhotoSchema(BaseModel):
    user_photo: UploadFile


    @field_validator('user_photo')
    @classmethod
    def validate_user_photo(cls, value):
        allowed_extensions = {'jpeg','jpg','png'}
        filename = value.filename.lower()
        parts = filename.split('.')
        if len(parts) > 2 :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file name: Double extensions are not allowed. No more than one dot allowed."
            )
        ext = parts[-1]
        if ext not in allowed_extensions:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Only jpeg, jpg, and png files are allowed for images.')
        return value 
    




class UpdatePassword(BaseModel):
    new_password:str 
    confirm_password: str
    class Config:
        extra = 'forbid'


    @field_validator('new_password')
    @classmethod
    def validate_password(cls,value):
        return validate(value)
    
    @model_validator(mode='before')
    @classmethod
    def validate(cls,values):
        if values.get('new_password') != values.get('confirm_password'):
            raise ValueError('Passwords do not match')
        return values

# schmea for product


PriceField = Annotated[Decimal, Field(gt=0, max_digits=7, decimal_places=2)]

class ProductSchemaCreate(BaseModel):
    product_title: str = Field(..., max_length=100)
    description: str
    price: PriceField

    class Config:
        extra = 'forbid'

class ProductImageCreate(BaseModel):
    images: List[UploadFile] 
    product_id:UUID 
    
    class Config:
        extra = 'forbid'
 

    @field_validator('images')
    @classmethod
    def validate_images(cls,value):
        # list of images
        allowed_extensions=['jpg','png','jepg']
        for image in value:
            filename = image.filename.lower()
            parts = filename.split('.')
            if len(parts) > 2 :
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file: No more than one dot allowed in the file name."
                )
            ext = parts[-1]
            if ext not in allowed_extensions:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail='only jpg,png,jpeg extenstions allowed'           )
            return value
        

        

 
