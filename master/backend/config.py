"""
Configuration settings for Master backend
"""

import os
from pathlib import Path
from typing import List

# Application settings
APP_TITLE = "Master Agent Manager"
APP_VERSION = "1.0.0"

# CORS settings
CORS_ORIGINS: List[str] = ["*"]  # In production, restrict to specific domains
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Static files paths (frontend build)
FRONTEND_DIST_PATHS = [
    Path(__file__).parent.parent / "frontend" / "dist",
    Path("/app/frontend/dist"),  # Docker path
    Path("frontend/dist"),  # Alternative path
]

# Database settings (from environment or defaults)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./master.db"  # Default to SQLite for development
)

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"  # Development mode

