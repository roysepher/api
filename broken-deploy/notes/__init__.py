from flask import Flask, jsonify

from .config import CONFIGS
from .extensions import db


def create_app(config_name="production"):
    app = Flask(__name__)
    config = CONFIGS[config_name]
    config.check()
    app.config.from_object(config)

    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify(error={"code": "not_found", "message": "No such route."}), 404

    return app
