import os


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    JWT_SECRET = os.environ.get("JWT_SECRET")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    @classmethod
    def check(cls):
        missing = [name for name in ("DATABASE_URL", "JWT_SECRET")
                   if not os.environ.get(name)]
        if missing:
            raise RuntimeError(
                "Missing required environment variable(s): " + ", ".join(missing)
            )


CONFIGS = {"production": ProductionConfig}
