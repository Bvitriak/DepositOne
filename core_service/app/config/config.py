import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]

def load_env() -> None:
    root = _project_root()
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value.strip()

def _require_int(name: str) -> int:
    raw = _require_env(name)
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(
            f"Environment variable {name} must be an integer, got: {raw!r}"
        ) from None

def get_flask_config() -> dict:
    load_env()
    jwt_expires_minutes = _require_int("JWT_ACCESS_TOKEN_EXPIRES")
    return {
        "SECRET_KEY": _require_env("SECRET_KEY"),
        "JWT_SECRET_KEY": _require_env("JWT_SECRET_KEY"),
        "JSON_AS_ASCII": False,
        "ENV": os.getenv("FLASK_ENV", "production").strip(),
        "DEBUG": os.getenv("FLASK_DEBUG", "0").strip() == "1",
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=jwt_expires_minutes),
    }
