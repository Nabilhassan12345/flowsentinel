"""
FlowSentinel Production Configuration
======================================
Environment-specific configuration for production deployment.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings with environment variable support."""
    
    # ==========================================================================
    # Core Application Settings
    # ==========================================================================
    APP_NAME: str = "FlowSentinel"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ==========================================================================
    # Security Settings
    # ==========================================================================
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Rate Limiting (per minute)
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # ==========================================================================
    # Database Settings
    # ==========================================================================
    DATABASE_URL: Optional[str] = None
    
    # ==========================================================================
    # Redis Settings (for caching and rate limiting)
    # ==========================================================================
    REDIS_URL: Optional[str] = None
    
    # ==========================================================================
    # IBM watsonx.ai Settings
    # ==========================================================================
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL_ID: str = "ibm/granite-3-8b-instruct"
    
    # ==========================================================================
    # Agent Settings
    # ==========================================================================
    AGENT_ENABLED: bool = True
    AGENT_RUN_INTERVAL: int = 300  # 5 minutes
    
    # ==========================================================================
    # Worker Pool Settings
    # ==========================================================================
    NUM_WORKERS: int = 4
    WORKER_QUEUE_SIZE: int = 1000
    
    # ==========================================================================
    # Slack Integration
    # ==========================================================================
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_BOT_TOKEN: Optional[str] = None
    
    # ==========================================================================
    # CORS Settings
    # ==========================================================================
    CORS_ORIGINS: str = "*"  # Comma-separated list or "*"
    
    # ==========================================================================
    # Monitoring Settings
    # ==========================================================================
    HEALTH_CHECK_INTERVAL: int = 30
    METRICS_ENABLED: bool = True
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            APP_NAME=os.getenv("APP_NAME", "FlowSentinel"),
            APP_VERSION=os.getenv("APP_VERSION", "2.0.0"),
            ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8000")),
            SECRET_KEY=os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production"),
            JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
            JWT_EXPIRATION_HOURS=int(os.getenv("JWT_EXPIRATION_HOURS", "24")),
            RATE_LIMIT_REQUESTS=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            RATE_LIMIT_WINDOW_SECONDS=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
            DATABASE_URL=os.getenv("DATABASE_URL"),
            REDIS_URL=os.getenv("REDIS_URL"),
            WATSONX_API_KEY=os.getenv("WATSONX_API_KEY"),
            WATSONX_PROJECT_ID=os.getenv("WATSONX_PROJECT_ID"),
            WATSONX_URL=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            WATSONX_MODEL_ID=os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct"),
            AGENT_ENABLED=os.getenv("AGENT_ENABLED", "true").lower() == "true",
            AGENT_RUN_INTERVAL=int(os.getenv("AGENT_RUN_INTERVAL", "300")),
            NUM_WORKERS=int(os.getenv("NUM_WORKERS", "4")),
            WORKER_QUEUE_SIZE=int(os.getenv("WORKER_QUEUE_SIZE", "1000")),
            SLACK_WEBHOOK_URL=os.getenv("SLACK_WEBHOOK_URL"),
            SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN"),
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "*"),
            HEALTH_CHECK_INTERVAL=int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
            METRICS_ENABLED=os.getenv("METRICS_ENABLED", "true").lower() == "true",
        )


# Singleton settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def is_production() -> bool:
    """Check if running in production environment."""
    return get_settings().ENVIRONMENT.lower() in ["production", "prod"]


def is_development() -> bool:
    """Check if running in development environment."""
    return get_settings().ENVIRONMENT.lower() in ["development", "dev", "local"]


# Environment-specific configuration templates
PRODUCTION_CONFIG = {
    "ENVIRONMENT": "production",
    "DEBUG": False,
    "RATE_LIMIT_REQUESTS": 100,
    "AGENT_RUN_INTERVAL": 300,
    "NUM_WORKERS": 8,
}

DEVELOPMENT_CONFIG = {
    "ENVIRONMENT": "development",
    "DEBUG": True,
    "RATE_LIMIT_REQUESTS": 1000,  # Higher for testing
    "AGENT_RUN_INTERVAL": 60,    # Faster for development
    "NUM_WORKERS": 2,
}

TESTING_CONFIG = {
    "ENVIRONMENT": "testing",
    "DEBUG": True,
    "RATE_LIMIT_REQUESTS": 10000,  # No limit for tests
    "AGENT_ENABLED": False,        # Disable agent in tests
    "NUM_WORKERS": 1,
}
