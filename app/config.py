from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    SECRET: str
    ALGORITHM : str  
    class Config:
        env_file='.env'

settings = Settings()