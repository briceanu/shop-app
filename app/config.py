from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    SECRET: str
    ALGORITHM : str  
    REFRESH_SECRET:str
    MAIL_USERNAME :str 
    MAIL_PASSWORD :str
    MAIL_FROM :str
    MAIL_PORT :str
    MAIL_SERVER :str
    MAIL_FROM_NAME :str
    MAIL_STARTTLS :str
    MAIL_SSL_TLS :str
    USE_CREDENTIALS :str
    VALIDATE_CERTS :str



    class Config:
        env_file='.env'

settings = Settings()