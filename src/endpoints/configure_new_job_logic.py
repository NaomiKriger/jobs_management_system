from http import HTTPStatus
from typing import Optional

from flask import Response, make_response, request
from pydantic import (ValidationError)

from src.consts import Endpoint
from src.database import add_entry, db, read_table
from src.endpoints.commons import get_event_names_from_db
from src.endpoints.configure_new_job_entity import JobConfigurationRequest
from src.models.event import Event
from src.models.job import Job
from src.models.job_in_event import JobInEvent


def get_input_event_names_that_are_not_found_in_db():
    input_event_names = request.json["event_names"]
    input_event_names_found_in_db = get_event_names_from_db(input_event_names)
    input_events_that_are_not_in_db = set(input_event_names) - set(
        event.event_name for event in input_event_names_found_in_db
    )
    return input_events_that_are_not_in_db


class ConfigureJobValidations:
    @staticmethod
    def validate_job_parameters() -> Optional[Response]:
        try:
            JobConfigurationRequest.parse_obj(request.json)
        except ValidationError as e:
            error_message = ""
            # error['loc'][-1] is the field's name
            for error in e.errors():
                prefix = (
                    f"{error['loc'][-1]}: " if error["loc"][-1] != "__root__" else ""
                )
                error_message = ", ".join(
                    [f"{prefix}" f"{error['msg']}" for error in e.errors()]
                )
            return make_response(error_message, HTTPStatus.BAD_REQUEST)

        notes = []
        input_events_that_are_not_found_in_db = (
            get_input_event_names_that_are_not_found_in_db()
        )
        if input_events_that_are_not_found_in_db:
            notes.append(
                f"the following event names were not found in DB and therefore "
                f"the job wasn't connected to them: {list(input_events_that_are_not_found_in_db)}"
            )
        return make_response(f"Job configured. Notes:{notes}", HTTPStatus.OK)


def get_events_from_db_per_event_names(event_names: set) -> set:
    events = read_table(Event)
    events_to_return = set()
    for event in events:
        if event.event_name in event_names:
            events_to_return.add(event)
    return events_to_return


def add_record_to_job_table():
    events_found_in_db = Event.query.filter(
        Event.event_name.in_(request.json["event_names"])
    ).all()
    events_to_connect = [event.event_name for event in events_found_in_db]
    add_entry(
        Job(
            request.json["image_tag"],
            request.json["schema"],
            events_to_connect,
            request.json["expiration_days"],
        ),
        db,
    )


def add_record_to_job_in_event_table():
    job = Job.query.filter_by(image_tag=request.json["image_tag"]).first()
    event_names_found_in_db = get_events_from_db_per_event_names(
        request.json["event_names"]
    )
    for event in event_names_found_in_db:
        add_entry(JobInEvent(job, event), db)


def configure_new_job_response():
    validation_response = ConfigureJobValidations.validate_job_parameters()
    if validation_response.status_code != HTTPStatus.OK:
        return validation_response

    add_record_to_job_table()
    add_record_to_job_in_event_table()

    return make_response(
        f"{Endpoint.CONFIGURE_NEW_JOB.value[1:]} finished successfully. "
        f"{validation_response.get_data().decode('utf-8')}",
        HTTPStatus.OK,
    )
