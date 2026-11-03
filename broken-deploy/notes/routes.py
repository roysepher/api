from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .extensions import db
from .models import Note

bp = Blueprint("notes", __name__)
_tables_ready = False


def error(code, message, status):
    return jsonify(error={"code": code, "message": message}), status


@bp.before_app_request
def connect_database():
    """Check the database on every request; create the table the first time."""
    global _tables_ready
    try:
        db.session.execute(text("SELECT 1"))
        if not _tables_ready:
            db.create_all()  # kept simple for this exercise; your own project uses migrations
            _tables_ready = True
    except OperationalError as exc:
        db.session.rollback()
        current_app.logger.error("Database connection failed: %s", exc.orig)
        return error("database_unavailable", "The app cannot reach its database.", 503)


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/notes")
def list_notes():
    notes = Note.query.order_by(Note.id).all()
    return jsonify(notes=[n.to_dict() for n in notes])


@bp.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    note_text = (data.get("text") or "").strip()
    if not note_text:
        return error("validation_error", "Field 'text' is required.", 400)
    note = Note(text=note_text[:280])
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201
