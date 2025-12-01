import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Fin Risk Analyzer API"
    
    # LLM Settings
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://host.docker.internal:12434/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "unused")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "llama-3.2-3b")

    class Config:
        case_sensitive = True

settings = Settings()
