from src.database import db


class JobsInEvents(db.Model):
    __tablename__ = "jobs_in_events"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    job = db.relationship(
        "Jobs", backref=db.backref("jobs_in_events", cascade="all, delete-orphan")
    )
    event = db.relationship(
        "Events", backref=db.backref("jobs_in_events", cascade="all, delete-orphan")
    )

    def __init__(self, job, event):
        self.job = job
        self.event = event

    def __repr__(self):
        return "<Jobs in events: %r>" % self.title
