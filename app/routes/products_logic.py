from sqlalchemy.orm import Session , selectinload,joinedload
from models import User, ProductImage
from schemas import ProductSchemaCreate, ProductImageCreate
from sqlalchemy import insert, select, and_, update, delete
from models import Product, User, ProductImage
from fastapi import HTTPException,status
import uuid
import os, shutil


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
    return {'success':'image saved'}

 
def remove_product(
                    product_id:uuid.UUID,
                    session:Session,
                    user:User,
                    ):
    stmt = (delete(Product)
            .where(Product.product_id==product_id,
                   Product.user.username == user ))
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'no product with the id {product_id}')
    return {'success':'product removed'}