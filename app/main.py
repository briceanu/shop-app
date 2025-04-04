from fastapi import FastAPI
from routes.user_api import router as user_router
from routes.products_api import router as product_router


app = FastAPI()


app.include_router(user_router)
app.include_router(product_router)



