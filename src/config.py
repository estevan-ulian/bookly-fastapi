from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_DOMAIN: str
    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 9993

    ALLOWED_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str = "Bookly"
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


Config = Settings()  # type: ignore
