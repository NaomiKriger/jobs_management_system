from sqlalchemy import JSON

from src.database import db


class Job(db.Model):
    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    image_tag = db.Column(db.String(80), unique=True, nullable=False)
    schema = db.Column(JSON, nullable=False)
    event_names = db.Column(JSON, nullable=False)  # TODO: list of string
    expiration_days = db.Column(db.Integer)

    def __init__(
        self, image_tag: str, schema: dict, event_names: list, expiration_days: int
    ):
        self.image_tag = image_tag
        self.schema = schema
        self.event_names = event_names
        self.expiration_days = expiration_days

    def __repr__(self):
        return "<Job: %r>" % self.title
