import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI JOB HUNTER"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ai-job-hunter-super-secret-key-2026-secure-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_job_hunter.db")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama3.2:3b")

    STORAGE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
    MASTER_RESUME_DIR: str = os.path.join(STORAGE_DIR, "master_resume")
    GENERATED_RESUME_DIR: str = os.path.join(STORAGE_DIR, "generated_resumes")

    class Config:
        case_sensitive = True

settings = Settings()

