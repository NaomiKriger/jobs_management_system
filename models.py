from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(80), unique=True, nullable=False)
    schema = db.Column(JSON, nullable=False)

    def __init__(self, event_name, schema):
        self.event_name = event_name
        self.schema = schema

    def __repr__(self):
        return "<Event: %r>" % self.title


class Job(db.Model):
    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(80), unique=True, nullable=False)
    schema = db.Column(JSON, nullable=False)
    event_names = db.Column(db.String(80), nullable=False)  # TODO: list of string
    path_to_job_content = db.Column(db.String(80), nullable=False)  # TODO: ECR path
    expiration_days = db.Column(db.Integer)

    def __init__(
        self, job_name, schema, event_names, path_to_job_content, expiration_days
    ):
        self.job_name = job_name
        self.schema = schema
        self.event_names = event_names
        self.path_to_job_content = path_to_job_content
        self.expiration_days = expiration_days

    def __repr__(self):
        return "<Job: %r>" % self.title


class JobInEvent(db.Model):
    __tablename__ = "job_in_event"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    job = db.relationship(
        "Job", backref=db.backref("job_in_event", cascade="all, delete-orphan")
    )
    event = db.relationship(
        "Event", backref=db.backref("job_in_event", cascade="all, delete-orphan")
    )

    def __init__(self, job, event):
        self.job = job
        self.event = event

    def __repr__(self):
        return "<Job in event: %r>" % self.title
