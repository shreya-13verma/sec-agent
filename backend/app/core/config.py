"""Application Configuration."""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SUSE MLM Security & Compliance Agent"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sec_agent.db")
    MCP_SERVER_NAME: str = "suse-mlm-security"
    APPROVAL_TOKEN_TTL_SECONDS: int = 900  # 15 minutes default
    COMPLIANCE_TIMEOUT_SECONDS: int = 300
    AUDIT_RETENTION_DAYS: int = 365
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True

settings = Settings()
