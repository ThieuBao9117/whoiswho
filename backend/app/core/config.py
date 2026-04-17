try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    USE_PYDANTIC_SETTINGS = True
except ImportError:
    from pydantic import BaseModel as BaseSettings
    USE_PYDANTIC_SETTINGS = False

class Settings(BaseSettings):
    PROJECT_NAME: str = "ConnectReward API"
    DATABASE_URL: str = "sqlite:///./connectreward.db"
    SECRET_KEY: str = "your-secret-key-for-dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200 # 30 days
    SYNOLOGY_WEBHOOK_URL: str = ""

    if USE_PYDANTIC_SETTINGS:
        model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
