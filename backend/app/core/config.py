from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hr Policy & Onboarding Bot"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str
    QDRANTO_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
