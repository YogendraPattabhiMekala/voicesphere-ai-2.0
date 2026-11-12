from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret_key: str = "insecure-development-key-change-me-please"
    database_url: str = "sqlite:///./voicesphere.db"
    access_token_minutes: int = 60
    cors_origins: str = "http://localhost:3000"
    voice_mode: str = "mock"
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")


settings = Settings()
