import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_local_env():
    """Load simple KEY=value pairs locally without adding a runtime dependency."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()


class Config:
    _is_production = os.environ.get("FLASK_ENV") == "production"
    _secret_key = os.environ.get("SECRET_KEY")
    if _is_production and not _secret_key:
        raise RuntimeError("SECRET_KEY must be configured in production.")
    SECRET_KEY = _secret_key or "local-development-only-not-for-production"
    _database_url = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'retro_game.db'}")
    # Older hosts sometimes expose the historic postgres:// prefix.
    SQLALCHEMY_DATABASE_URI = _database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    MAX_CONTENT_LENGTH = 16 * 1024
