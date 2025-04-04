from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            column_property,
                            relationship,
                            )

from sqlalchemy import String, DECIMAL, func, ForeignKey, Integer
import uuid
from typing import List
from datetime import datetime

class Base(DeclarativeBase):
    ...

# alemibc revision --autogenerate -m 'initial revision'


# this is the model for the user

 

class User(Base):
    __tablename__= 'user'

    user_id: Mapped[uuid.UUID] = mapped_column(default=lambda:uuid.uuid4(),primary_key=True,unique=True)
    username: Mapped[str] = mapped_column(String(60),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(nullable=True)
    # this filed is only for learning about column_property
    welcome_message: Mapped[str] = column_property(
        func.concat("Welcome to our shop ", username, "!!!"))
    balance:Mapped[float] = mapped_column(DECIMAL(5,2),nullable=True)
    user_photo:Mapped[str] = mapped_column(String(),nullable=True)
    address:Mapped[str] = mapped_column(String(),nullable=True)
    products: Mapped[List['Product']] = relationship('Product', back_populates='user')
 
 
class Product(Base):
    __tablename__ = 'product'

    product_id:Mapped[uuid.UUID]= mapped_column(default=lambda:uuid.uuid4(),primary_key=True,unique=True)
    product_title:Mapped[str]= mapped_column(String(100))
    description:Mapped[str]=mapped_column()
    price:Mapped[int] = mapped_column(DECIMAL(5,2),nullable=False)
    images:Mapped[List['ProductImage']]= relationship('ProductImage',
                    back_populates='product',cascade='all,delete-orphan')
    user:Mapped['User'] = relationship('User',back_populates='products')
    user_id:Mapped[uuid.UUID] = mapped_column(ForeignKey('user.user_id'),nullable=False)
  

class ProductImage(Base):
    __tablename__ = 'product_image'

    image_id:Mapped[uuid.UUID]= mapped_column(default=lambda: uuid.uuid4(),primary_key=True,unique=True)    
    image_url:Mapped[str]=mapped_column(String,nullable=False)
    product_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('product.product_id'),nullable=False)
    product:Mapped['Product']=relationship('Product',back_populates='images')



# OrderTable