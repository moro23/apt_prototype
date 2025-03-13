import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "eAPPRAISAL MANAGEMENT SYSTEM"
    PROJECT_VERSION: str = "1.0.0"

    SMS_API_KEY: str
    SMS_API_URL: str

    intruder_list: list = []

    MAX_CONCURRENT_THREADS: int = 10  # Maximum number of concurrent threads
    MAX_RETRIES: int = 1  # Maximum number of retry attempts
    RETRY_DELAY_BASE: int = 0  # Initial retry delay in seconds
    RETRY_DELAY_MULTIPLIER: int = 1  # Exponential backoff multiplier

    set_allow_origin: str = "http://localhost:4200, https://performance-appraisal.netlify.app"

    POSTGRES_PASSWORD: str
    SQLALCHEMY_DATABASE_URL: str

    INSTANCE_CONNECTION_NAME: Optional[str] = None
    UNIX_SOCKET: str = '/cloudsql/'
    PROJECT_ID: str = "smartconference-404416"
    BUCKET_NAME: str = "developers-bucket"
    IMAGE_PATH: str = "developers-bucket/test-app/file_path/media/images"
    DOCUMENT_PATH: str = "developers-bucket/test-app/file_path/docs"
    AUDIO_PATH: str = "developers-bucket/test-app/file_path/media/audios"
    VIDEO_PATH: str = "developers-bucket/test-app/file_path/media/videos"
    SHOW_DOCS: bool = True
    ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", set_allow_origin)
    SET_NEW_ORIGIN: list = ALLOW_ORIGINS.split(',')
    SYSTEM_LOGO: str

    MAIL_USERNAME: str = 'dev.aiti.com.gh@gmail.com'
    MAIL_PASSWORD: str = ''
    MAIL_FROM: str = "dev.aiti.com.gh@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = 'smtp.gmail.com'
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    FRONTEND_URL: str

    EMAIL_CODE_DURATION_IN_MINUTES: int = 15
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    REFRESH_TOKEN_DURATION_IN_MINUTES: int = 43800
    REFRESH_TOKEN_REMEMBER_ME_DAYS: int = 5184000  # or any appropriate value
    COOKIE_ACCESS_EXPIRE: int = 1800
    COOKIE_REFRESH_EXPIRE: int = 2592000  # 1 Month
    COOKIE_DOMAIN: str = "gikace.dev"
    PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES: int = 15
    ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES: int = 15

    POOL_SIZE: int = 20
    POOL_RECYCLE: int = 3600
    POOL_TIMEOUT: int = 15
    MAX_OVERFLOW: int = 2
    CONNECT_TIMEOUT: int = 60
    connect_args: dict = {"connect_timeout": CONNECT_TIMEOUT}

    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    REFRESH_TOKEN_SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=f"{Path().resolve()}/.env",
        case_sensitive=True,
        validate_assignment=True,
        extra="allow",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
