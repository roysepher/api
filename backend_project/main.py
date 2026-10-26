from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.route("/")
def index():
    return "ok"
