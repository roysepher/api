from flask import Flask

from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import db, migrate

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    migrate.init_app(app, db)

    from .main import bp

    app.register_blueprint(bp)
    return app