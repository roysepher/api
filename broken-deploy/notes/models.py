from .extensions import db


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(280), nullable=False)

    def to_dict(self):
        return {"id": self.id, "text": self.text}
