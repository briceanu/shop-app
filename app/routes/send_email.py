from fastapi import  BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from config import settings

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME, 
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = settings.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.VALIDATE_CERTS
)
 

async def send_in_background(
    email: List[str], background_tasks: BackgroundTasks, username: str
):
    message = MessageSchema(
        subject=f"Welcome {username}",
        recipients=email,
        body="On behalf of our team, we wish you a very nice day.",
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)  # Add email task to background




