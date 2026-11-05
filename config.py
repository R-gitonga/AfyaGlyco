import os

from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'dev.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", "1") == "1"

