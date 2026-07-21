"""
Central place for application configuration.

All secrets and environment-dependent values (signing keys, DB credentials,
token lifetime, etc.) are read from environment variables / the local
`.env` file instead of being hardcoded in the source code.

Copy `.env_example` to `.env` and fill in real values before running
the application. `.env` is git-ignored, so real secrets never get committed.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# app/core/config.py -> app/core -> app -> <project root>
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    OLLAMA_URL: str = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434",
    )

    def __init__(self) -> None:
        if not self.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY is not set. Copy .env_example to .env and set a real value."
            )
        if not self.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is not set. Copy .env_example to .env and set a real value."
            )


settings = Settings()
