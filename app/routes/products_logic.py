from sqlalchemy.orm import Session ,joinedload, load_only
from models import User, ProductImage, Order, OrderItem
from schemas import ProductSchemaCreate, ProductImageCreate, OrderItemSchema
from sqlalchemy import insert, select, desc,func,case
from models import Product, User, ProductImage
from fastapi import HTTPException,status
import uuid
import os, shutil
from decimal import Decimal
from tasks import generate_pdf_and_send_email
from pydantic import PositiveInt
from sqlalchemy import cast,Integer

def upload_product(
                product:ProductSchemaCreate,
                session:Session,
                user:User,
                 ):
    user_id_from_db=session.execute(select(User.user_id).where(User.username==user)).scalar()
    if not user_id_from_db:
        raise HTTPException(status_code=status.http404,
                            detail=f'no user with the username {user} found.')
    stmt = insert(Product).values(
        **product.model_dump(),
        user_id= user_id_from_db
        )
    session.execute(stmt)
    session.commit()
    return {'success':'product saved'}
    
def list_products(session:Session,user:User):
    user_id_from_db = session.execute(select(User.user_id).where(User.username==user)).scalar()
    stmt = (select(Product)
            .where(Product.user_id==user_id_from_db)
            .options(joinedload(Product.images))
            )
    products = session.execute(stmt).unique().scalars().all()
    return products

 
def image_upload(
    data: ProductImageCreate,
    session: Session,
    user: User,
):

    # Validate the user
    user_id_from_db = session.execute(
        select(User.user_id).where(User.username == user) 
    ).scalar()

    if not user_id_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with the username {user.username} found.",
        )

    # Create upload directory
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    for image in data.images:  # Loop through multiple images
        file_path = os.path.join(UPLOAD_DIR, image.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Store the image URL in the database
        stmt = insert(ProductImage).values(
            product_id=data.product_id,
            image_url=file_path
        )
        session.execute(stmt)
    # Commit the transaction after inserting all images
    session.commit()
    return {'success':'product updated'}

 
def remove_product(
                    product_id:uuid.UUID,
                    session:Session,
                    user:User,
                    ):

    user_id = session.execute(select(User.username).where(User.username==user)).scalar_one_or_none()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='not allowed to perform this action') 
    

    product = session.execute(
        select(Product).where(Product.product_id == product_id)
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product with ID {product_id} not found'
        )

    if product.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this product")
    session.delete(product)
    session.commit()
    return {'success':'product removed'}




def place_order(data: OrderItemSchema, session: Session, user: User):
    # Fetch user ID based on the username
    user_from_db = (
        session.execute(select(User)
                        .options(load_only(User.user_id,User.balance))
                        .where(User.username == user))
        .scalar_one_or_none()
    )
    if not user_from_db:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN
                            ,detail='not allowed to preform this action')
    # Fetch valid products from the database
    valid_products_from_db = session.execute(
        select(Product)
        .where(Product.product_id.in_([product.product_id for product in data.products]))
    ).scalars().all()


    # Convert valid products into a dictionary for quick lookup by product_id
    valid_products_dict = {product.product_id: product for product in valid_products_from_db}

    # Create a list of order items
    order_items = []
    price_per_items=[]
    item_data_for_pdf = []
    # Iterate through the products in the client's request
    for product in data.products:
        db_product = valid_products_dict.get(product.product_id)
        
        # If the product doesn't exist in the database, raise an error
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Product with id {product.product_id} is not valid.'
            )
      

    # validating if there are enough items in the db
    for product in data.products:
        db_product = valid_products_dict.get(product.product_id)
        if product.quantity > db_product.quantity:
          raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with id {product.product_id} has only {db_product.quantity} left in stock."
            )
        # remove the bought items from the db
        db_product.quantity -= product.quantity
        # Create an OrderItem instance for each valid product
        order_items.append(
            OrderItem(
                product_id=product.product_id,
                quantity=product.quantity,  # Use the quantity provided by the client
                price_at_order_time=db_product.price,  # Use the price from the DB
                amount = product.quantity * db_product.price
            )
        )
        price_per_items.append(float(product.quantity * db_product.price))
        item_data_for_pdf.append({
        "name": db_product. product_title,
        "quantity": product.quantity,
        "price": db_product.price
        })
    # validating the user balance
    if user_from_db.balance < sum(price_per_items):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"not enought money to buy the products. Balance:{user_from_db.balance} Cost:{round(sum(price_per_items), 2)}"
            ) 
 
    #create pdf_file 
    # send email with the purchased items

    # Create an Order instance
    new_order = Order(
        user_id= user_from_db.user_id,
        order_items=order_items,  # Add the list of order items to the order
        total_amount=sum(price_per_items)
    )

    # decrease the users balance
    user_from_db.balance -= Decimal(sum(price_per_items))
    # Add the new order to the session and commit
    session.add(new_order)
    session.commit()


    #  Send PDF via Celery
    order_data_for_pdf = {
        "items": item_data_for_pdf,
        "total": Decimal(sum(price_per_items))
    }
    generate_pdf_and_send_email.delay(order_data_for_pdf, user_from_db.email)


    return {'success': 'Order placed successfully'}



 

def show_all_orders(session:Session):
    orders = (session.execute(
        select(Order)
        .options(joinedload(Order.order_items)))
        .unique().scalars().all())
    return orders

# filtering the products
def filter_products(filter:str,session:Session):
    # stmt = (select(Product).where(Product.product_title.ilike(f'%{filter}%')))
    # stmt = (select(Product).where(Product.product_title.startswith(filter)))
    stmt = (select(Product).where(Product.product_title.icontains(filter)))

    # stmt = (select(Product).where(Product.price > filter))    
    products = session.execute(stmt).scalars().all()
    return products

# filter by price
def filter_products(min_price:float,
                    max_price:float,
                    session:Session):

    stmt = (select(Product)
            .where(Product.price.between(min_price,max_price))
            .order_by(desc(Product.quantity))
            )
            

    products = session.execute(stmt).scalars().all()
    return products


# count all products
def count_products(session:Session):
    stmt = (select(func.sum(func.coalesce(Product.quantity,0))))
    total = session.execute(stmt).scalar()
    return {'total_products':total}

# count how many products are more expensive than 1000
def count_products_gt(price:PositiveInt,
                           session:Session):
    stmt = (select(
        func.sum(func.coalesce(Product.quantity,0)))
            .where(Product.price < price)
        )
    total = session.execute(stmt).scalar()
    return {'number_of_products':total}


# label the products

def label_products(session:Session):
    stmt = select(Product
                  ,case(
        (Product.price <1000,'cheap'),
        (Product.price >5000,'very expensive'),
        else_='I can afford').label('price_category')
        )
    
    result=session.execute(stmt).all()
    products = [{'product':product.product_title,'price_category':price_category}
                for product, price_category in result]

    return products



def expensive_product(session:Session):
    product = (session.execute(
        select(func.max(Product.price))).scalar_one())  
    return {'the_most_expensive':product}

# using the cast method to convert decimal to integer 

# def expensive_product(session:Session):
#     product = (session.execute(
#         select(func.max(cast(Product.price,Integer)))).scalar_one())  
#     return {'the_most_expensive':product}


# let's count all the products exclude null
def select_users(session:Session):

    stmt = select(func.count(User.user_id)).where(User.user_photo.is_not(None))
    number_of_users_with_photo = session.execute(stmt).scalar()
    return {'number_of_users':number_of_users_with_photo}
    


def select_data(session:Session):
    stmt = (select(Product)
            .options(joinedload(Product.images))
            .where(Product.price <1000,Product.quantity.is_not(None)).order_by(Product.quantity))
            
    products = session.execute(stmt).unique().scalars().all()

    return products


