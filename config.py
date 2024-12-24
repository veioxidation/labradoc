import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ExtractionApp"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/extraction_db"
    NUCLEUS_API_URL: str = "https://nucleus.example.com"
    NUCLEUS_API_KEY: str = "my-nucleus-api-key"

    class Config:
        env_file = ".env"  # optionally load environment variables from a file

settings = Settings()
