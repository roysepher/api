import os

from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig:
    DEBUG = True
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-placeholder")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")


class TestingConfig:
    TESTING = True
    JWT_SECRET = os.getenv("JWT_SECRET")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class ProductionConfig:
    DEBUG = False
    JWT_SECRET = os.getenv("JWT_SECRET")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
