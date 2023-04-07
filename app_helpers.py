from flask import request

from app_validations import UploadJobValidations
from database import add_entry
from models import Job, JobInEvent


def upload_job_to_container_registry(job):
    return "ecr_path"


def add_job_entry(job_path, db):
    add_entry(
        Job(
            request.json["job_name"],
            request.json["schema"],
            request.json["event_names"],
            job_path,
            request.json["expiration_days"],
        ),
        db,
    )


def add_job_to_job_in_event(db):
    job = Job.query.filter_by(job_name=request.json["job_name"]).first()
    event_names_found_in_db = UploadJobValidations.get_events_from_db_per_event_names(
        request.json["event_names"]
    )
    for event in event_names_found_in_db:
        add_entry(JobInEvent(job, event), db)
