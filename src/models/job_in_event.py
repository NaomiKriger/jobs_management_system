from src.database import db


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
