import os

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv()


def _database_uri(default=None):
    database_uri = os.getenv("DATABASE_URL", default)
    if database_uri is None:
        return None

    url = make_url(database_uri)
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    elif url.drivername == "postgres":
        url = url.set(drivername="postgresql+psycopg")
    return url.render_as_string(hide_password=False)


class DevelopmentConfig:
    DEBUG = True
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-placeholder")
    NEON_AUTH_BASE_URL = os.getenv("NEON_AUTH_BASE_URL")
    NEON_AUTH_JWKS_URL = os.getenv("NEON_AUTH_JWKS_URL")
    # Token lifetime is configured in seconds.
    JWT_LIFETIME_SECONDS = int(os.getenv("JWT_LIFETIME_SECONDS", "3600"))
    SQLALCHEMY_DATABASE_URI = _database_uri("sqlite:///dev.db")


class TestingConfig:
    TESTING = True
    JWT_SECRET = os.getenv("JWT_SECRET")
    NEON_AUTH_BASE_URL = os.getenv("NEON_AUTH_BASE_URL")
    NEON_AUTH_JWKS_URL = os.getenv("NEON_AUTH_JWKS_URL")
    # Token lifetime is configured in seconds.
    JWT_LIFETIME_SECONDS = int(os.getenv("JWT_LIFETIME_SECONDS", "3600"))
    SQLALCHEMY_DATABASE_URI = _database_uri()


class ProductionConfig:
    DEBUG = False
    JWT_SECRET = os.getenv("JWT_SECRET")
    NEON_AUTH_BASE_URL = os.getenv("NEON_AUTH_BASE_URL")
    NEON_AUTH_JWKS_URL = os.getenv("NEON_AUTH_JWKS_URL")
    # Token lifetime is configured in seconds.
    JWT_LIFETIME_SECONDS = int(os.getenv("JWT_LIFETIME_SECONDS", "3600"))
    SQLALCHEMY_DATABASE_URI = _database_uri()
