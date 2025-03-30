from fastapi import FastAPI
from routes.user_api import router as user_router



app = FastAPI()


app.include_router(user_router)



