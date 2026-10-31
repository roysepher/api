from flask import Flask

from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import db, migrate
from . import models
from .responses import error_response

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

    @app.errorhandler(400)
    def handle_bad_request(error):
        return error_response("bad_request", "bad request", 400)

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return error_response("unauthorized", "authentication required", 401)

    @app.errorhandler(403)
    def handle_forbidden(error):
        return error_response("forbidden", "access forbidden", 403)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("not_found", "resource not found", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return error_response("method_not_allowed", "method not allowed", 405)

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        return error_response("server_error", "internal server error", 500)

    from .auth.routes import bp as auth_bp
    from .main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app