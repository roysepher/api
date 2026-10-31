from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from ..db_errors import is_username_unique_violation
from ..extensions import db
from ..models import User
from ..responses import error_response
from .decorators import require_auth

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response(
            "invalid_field",
            "request body must be a JSON object",
            400,
        )
    if not isinstance(data.get("username"), str) or not isinstance(data.get("password"), str):
        return error_response(
            "invalid_field",
            "username and password are required",
            400,
        )

    username = data["username"].strip()
    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()
    if user is None or not check_password_hash(user.password_hash, data["password"]):
        return error_response(
            "invalid_credentials",
            "username or password is incorrect",
            401,
        )

    jwt_secret = current_app.config["JWT_SECRET"]
    jwt_lifetime_seconds = current_app.config["JWT_LIFETIME_SECONDS"]
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "exp": now + timedelta(seconds=jwt_lifetime_seconds),
        },
        jwt_secret,
        algorithm="HS256",
    )
    return jsonify(access_token=token, token_type="Bearer"), 200


@bp.post("/register")
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response(
            "invalid_field",
            "request body must be a JSON object",
            400,
        )
    if "username" not in data:
        return error_response("missing_field", "username is required", 400)
    if "password" not in data:
        return error_response("missing_field", "password is required", 400)

    if not isinstance(data["username"], str):
        return error_response("invalid_field", "username must be a string", 400)
    username = data["username"].strip()
    if not 3 <= len(username) <= 80:
        return error_response(
            "invalid_field",
            "username must be between 3 and 80 characters",
            400,
        )

    if not isinstance(data["password"], str):
        return error_response("invalid_field", "password must be a string", 400)
    if not 12 <= len(data["password"]) <= 128:
        return error_response(
            "invalid_field",
            "password must be between 12 and 128 characters",
            400,
        )

    user = User(
        username=username,
        password_hash=generate_password_hash(data["password"]),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        if not is_username_unique_violation(error):
            raise
        return error_response(
            "duplicate_username",
            "username is already taken",
            409,
        )

    return jsonify(
        id=user.id,
        username=user.username,
        created_at=user.created_at.isoformat(),
    ), 201


@bp.get("/whoami")
@require_auth
def whoami():
    return jsonify(user_id=g.user_id, role=g.role)
