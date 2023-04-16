from sqlalchemy import JSON

from src.database import db


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(80), unique=True, nullable=False)
    schema = db.Column(JSON, nullable=False)

    def __init__(self, event_name: str, schema: dict):
        self.event_name = event_name
        self.schema = schema

    def __repr__(self):
        return "<Event: %r>" % self.title
