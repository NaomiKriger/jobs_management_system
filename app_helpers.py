import os

from flask import request

from app_validations import ConfigureJobValidations
from database import add_entry
from models.event import Event
from models.job import Job
from models.job_in_event import JobInEvent


def add_job_entry(db):
    events_found_in_db = Event.query.filter(
        Event.event_name.in_(request.json["event_names"])).all()
    events_to_connect = [event.event_name for event in events_found_in_db]
    add_entry(
        Job(request.json["image_tag"], request.json["schema"], events_to_connect,
            request.json["expiration_days"]),
        db,
    )


def add_job_to_job_in_event(db):
    job = Job.query.filter_by(image_tag=request.json["image_tag"]).first()
    event_names_found_in_db = ConfigureJobValidations.get_events_from_db_per_event_names(
        request.json["event_names"]
    )
    for event in event_names_found_in_db:
        add_entry(JobInEvent(job, event), db)


def get_execution_flags() -> list:
    flags = []
    execution_parameters = request.json.get("execution_parameters")
    for key, value in execution_parameters.items():
        flags.append(f"--{key}")
        flags.append(str(value))
    return flags


def get_execution_command():
    ecr_path = os.getenv("ECR_PATH")
    repository_name = os.getenv("ECR_REPOSITORY_NAME")
    image_tag = request.json.get("image_tag")
    executable_file_name = request.json.get("executable_file_name")

    cmd = [
        "docker",
        "run",
        f"{ecr_path}/{repository_name}:{image_tag}",
        "python",
        f"{executable_file_name}",
    ]
    cmd += get_execution_flags()

    return cmd
