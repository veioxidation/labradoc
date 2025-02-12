import os
from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ExtractionApp"
    SCHEMA_NAME: str = "extraction"
    DATABASE_URL: Optional[str] = None
    NUCLEUS_API_URL: Optional[str] = None
    NUCLEUS_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"  # optionally load environment variables from a file

settings = Settings()
print(os.getenv('DATABASE_URL'))