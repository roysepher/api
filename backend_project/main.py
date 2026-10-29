from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from .auth.decorators import require_auth, require_role
from .extensions import db
from .models import Note, User
from .responses import error_response

bp = Blueprint("main", __name__)


def _profile_response(user):
    return jsonify(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at.isoformat(),
    )


@bp.get("/me")
@require_auth
def me():
    return jsonify(user_id=g.user_id)


@bp.post("/notes")
@require_auth
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response(
            "invalid_field",
            "request body must be a JSON object",
            400,
        )

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return error_response("invalid_field", "title must be a non-empty string", 400)
    title = title.strip()
    if len(title) > 200:
        return error_response(
            "invalid_field",
            "title must be at most 200 characters",
            400,
        )

    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        return error_response(
            "invalid_field",
            "content must be a non-empty string",
            400,
        )

    note = Note(user_id=g.user_id, title=title, content=content)
    db.session.add(note)
    db.session.commit()

    return jsonify(
        id=note.id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        created_at=note.created_at.isoformat(),
    ), 201


@bp.get("/notes")
@require_auth
def list_notes():
    notes = db.session.execute(
        db.select(Note).filter_by(user_id=g.user_id)
    ).scalars()
    return jsonify(
        [
            {
                "id": note.id,
                "user_id": note.user_id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat(),
            }
            for note in notes
        ]
    )


@bp.get("/notes/<int:note_id>")
@require_auth
def get_note(note_id):
    note = db.session.execute(
        db.select(Note).filter_by(id=note_id, user_id=g.user_id)
    ).scalar_one_or_none()
    if note is None:
        return error_response("note_not_found", "note not found", 404)

    return jsonify(
        id=note.id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        created_at=note.created_at.isoformat(),
    )


@bp.get("/admin")
@require_auth
@require_role("admin")
def admin():
    return jsonify(message="admin access granted", user_id=g.user_id, role=g.role)


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


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.route("/")
def index():
    return "ok"
