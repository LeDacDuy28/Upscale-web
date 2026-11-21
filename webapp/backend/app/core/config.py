"""Application settings and repository path bootstrap."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    STORAGE_DIR: Path = Path(
        os.getenv("STORAGE_DIR", str(BACKEND_ROOT / "storage"))
    ).resolve()
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "20"))
    MAX_IMAGE_DIM: int = int(os.getenv("MAX_IMAGE_DIM", "4096"))
    RETENTION_SECONDS: int = int(os.getenv("RETENTION_SECONDS", "3600"))
    DEFAULT_TILE_SIZE: int = int(os.getenv("DEFAULT_TILE_SIZE", "256"))
    ENABLE_FP16: bool = os.getenv("ENABLE_FP16", "true").lower() in ("1", "true", "yes")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    USE_REDIS_QUEUE: bool = os.getenv("USE_REDIS_QUEUE", "false").lower() in ("1", "true", "yes")
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:80"
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "inputs").mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "outputs").mkdir(parents=True, exist_ok=True)
