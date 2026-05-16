import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _build_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url
    user = os.environ.get("DB_USER", "quiz_user")
    password = os.environ.get("DB_PASSWORD", "")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "quiz_db")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

DEV_SECRET_KEY = "dev-secret-change-me"

@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    debug: bool
    pass_threshold: int
    excellent_threshold: int
    log_file: str | None
    admin_contact: str

settings = Settings(
    database_url=_build_database_url(),
    secret_key=os.environ.get("APP_SECRET_KEY", DEV_SECRET_KEY),
    debug=os.environ.get("DEBUG", "false").lower() == "true",
    pass_threshold=int(os.environ.get("PASS_THRESHOLD", "60")),
    excellent_threshold=int(os.environ.get("EXCELLENT_THRESHOLD", "80")),
    log_file=os.environ.get("LOG_FILE") or None,
    admin_contact=os.environ.get("ADMIN_CONTACT", "bitriak@gmail.com"),
)
