from flask import g, jsonify, request
from sqlalchemy.exc import IntegrityError

from ..auth.decorators import require_auth
from ..extensions import db
from ..models import User
from ..responses import error_response
from . import bp


def _profile_response(user):
    return jsonify(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at.isoformat(),
    )


@bp.get("/users/me")
@require_auth
def user_profile():
    user = db.session.get(User, g.user_id)
    if user is None:
        return error_response("user_not_found", "user not found", 404)

    return _profile_response(user)


@bp.patch("/users/me")
@require_auth
def update_user_profile():
    user = db.session.get(User, g.user_id)
    if user is None:
        return error_response("user_not_found", "user not found", 404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response(
            "invalid_field",
            "request body must be a JSON object",
            400,
        )
    if "username" in data:
        if not isinstance(data["username"], str):
            return error_response("invalid_field", "username must be a string", 400)
        username = data["username"].strip()
        if not 3 <= len(username) <= 80:
            return error_response(
                "invalid_field",
                "username must be between 3 and 80 characters",
                400,
            )
        user.username = username

    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        if (
            getattr(error.orig, "sqlite_errorname", None) != "SQLITE_CONSTRAINT_UNIQUE"
            or str(error.orig) != "UNIQUE constraint failed: user.username"
        ):
            raise
        return error_response(
            "duplicate_username",
            "username is already taken",
            409,
        )

    return _profile_response(user)
