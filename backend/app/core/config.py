from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GCP_PROJECT_ID: str = "casob-512514"
    GCP_REGION: str = "us-central1"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COST_THRESHOLD_USD: float = 0.05

    class Config:
        env_file = ".env"

settings = Settings()