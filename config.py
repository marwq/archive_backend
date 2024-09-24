from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_PORT: int

    # Postgres
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # Open AI
    OPENAI_TOKEN: str
    OPENAI_ASSISTANT_ID: str
    

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int

    # S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    AWS_BUCKET_NAME: str
    
    # REDIS
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASS: str

    # Google
    GOOGLE_AI_API_KEY: str

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str


settings = Settings()
