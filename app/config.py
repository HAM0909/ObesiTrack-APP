from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os



class Settings(BaseSettings):

    database_url: str = Field(
        default="postgresql://postgres:Chah%4015996@localhost:5432/obesittrack",
        env="DATABASE_URL"
    )

    secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    

    app_name: str = Field(default="ObesiTrack", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    

    postgres_db: str = Field(default="obesittrack", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres123", env="POSTGRES_PASSWORD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()