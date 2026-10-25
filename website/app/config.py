"""Settings read from the .env file.

[R9] Secrets (database password, session secret) are never written in the code.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")  # signs the session cookie
    SESSION_COOKIE_SAMESITE = "Lax"  # browser will not send the cookie on cross-site POSTs
    # [Bonus: deploy] on an https website set COOKIE_SECURE=1 so the cookie is never sent over http
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "0") == "1"

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "registration")        # Lab 2: users + todos

    # [Lab 3] the library database (Problem 2) lives in its own MySQL database
    LIBRARY_DB_NAME = os.getenv("LIBRARY_DB_NAME", "library")

    # [Lab 3, Bonus] book covers and author photos are saved here
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # a request bigger than 3 MB is refused
