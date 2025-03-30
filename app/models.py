from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            column_property)
from sqlalchemy import String, DECIMAL, func
import uuid
 

class Base(DeclarativeBase):
    ...




# this is the model for the user

# alemibc revision --autogenerate -m 'initial migration'

class User(Base):
    __tablename__= 'user'
# user_id , username, password, email , welcome string, balance, user_photo,address

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

