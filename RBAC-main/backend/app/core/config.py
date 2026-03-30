from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ROOT_EMAIL: str
    ROOT_PASSWORD: str
    DOC_EXTRACTOR_URL: str = "http://doc_extractor:8001"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()