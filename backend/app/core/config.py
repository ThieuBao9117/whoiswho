try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    USE_PYDANTIC_SETTINGS = True
except ImportError:
    from pydantic import BaseModel as BaseSettings
    USE_PYDANTIC_SETTINGS = False

class Settings(BaseSettings):
    PROJECT_NAME: str = "CSB Connection API"
    
    # PostgreSQL Database — use CSB_DATABASE_URL to avoid collision with
    # any system-level DATABASE_URL environment variable.
    CSB_DATABASE_URL: str = "postgresql+psycopg://postgres:123456@localhost:5433/hrm"
    
    # JWT Configuration
    SECRET_KEY: str = "csb-connection-secret-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Integration
    SYNOLOGY_WEBHOOK_URL: str = ""
    
    # HRM Sync Configuration
    HRM_API_URL: str = ""  # Optional: if CSB pulls from HRM instead of push
    HRM_API_KEY: str = ""

    if USE_PYDANTIC_SETTINGS:
        model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
