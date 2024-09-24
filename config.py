from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()



class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str


settings = Settings()
