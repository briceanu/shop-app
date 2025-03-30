from pydantic import (PositiveFloat,
                      BaseModel,
                      Field, 
                      field_validator,
                      model_validator
                      )
import re

class Base(BaseModel):
    ...




def validate(value):
    if len(value) < 6:
        raise ValueError('Password must be at least 6 characters long')
    if not re.search(r'[A-Za-z]', value):  # Check for at least one letter
        raise ValueError('Password must include at least one letter')
    if not re.search(r'\d', value): 
        raise ValueError('Password must contain at least one number')
    
    return value
     





class UserSignUpCreate(Base):
    username:str = Field(...,max_length=60)
    password:str 
    confirm_password: str
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