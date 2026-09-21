from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SUSE MLM Security & Compliance Agent"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "suse-mlm-compliance-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Database
    DATABASE_URL: str = "sqlite:////home/shreya/compliance-agent/compliance.db"
    
    # SUSE MLM Configuration
    SUSE_MLM_URL: str = "https://10.0.33.56/rhn/apidoc/index.jsp"
    SUSE_MLM_API_BASE: str = "https://10.0.33.56/rpc/api"
    SUSE_MLM_USER: str = "admin"
    SUSE_MLM_PASSWORD: str = "admin123"
    SUSE_MLM_MOCK_FALLBACK: bool = True
    
    # Operational & Domain Defaults
    SCAN_SCHEDULE_HOURS: int = 6
    SCAN_TIMEOUT_SECONDS: int = 300
    DATA_RETENTION_DAYS: int = 365
    CRITICAL_SCORE_THRESHOLD: float = 70.0
    MAX_CONCURRENT_REMEDIATIONS: int = 10

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
