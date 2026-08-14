# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    PROJECT_NAME: str = "DataRefine - CSV Cleaner & Importer"
    ENVIRONMENT: str = "development"
    API_KEY: SecretStr = Field(default=SecretStr("dev_secret_api_key_12345"))
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./dev_datarefine.db",
        env="DATABASE_URL"
    )
    
    # Processing Limits
    MAX_FILE_SIZE_BYTES: int = 52_428_800  # 50 MB
    CHUNK_SIZE_ROWS: int = 5000
    DEFAULT_PHONE_REGION: str = "US"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
