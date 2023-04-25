from http import HTTPStatus
from typing import Optional

from flask import Response, make_response

from src.consts import Endpoint
from src.database import db
from src.endpoints.common import (add_entry, get_event_names_from_db,
                                  validate_request_parameters)
from src.models.events import Events
from src.models.jobs import Jobs
from src.models.jobs_in_events import JobsInEvents
from src.serializers.configure_new_job import JobConfigurationRequest


def get_input_event_names_that_are_not_found_in_db(event_names: list) -> set:
    input_event_names = event_names
    input_event_names_found_in_db = get_event_names_from_db(input_event_names)
    input_events_that_are_not_in_db = set(input_event_names) - set(
        event.event_name for event in input_event_names_found_in_db
    )
    return input_events_that_are_not_in_db


def response_notes(request_body: dict) -> Optional[Response]:
    notes = []
    input_events_that_are_not_found_in_db = (
        get_input_event_names_that_are_not_found_in_db(request_body.get("event_names"))
    )
    if input_events_that_are_not_found_in_db:
        notes.append(
            f"the following event names were not found in DB and therefore "
            f"the job wasn't connected to them: {list(input_events_that_are_not_found_in_db)}"
        )
    return make_response(f"Job configured. Notes:{notes}", HTTPStatus.OK)


def get_events_from_db_per_event_names(event_names: set) -> set:
    events = Events.query.all()
    events_to_return = set()
    for event in events:
        if event.event_name in event_names:
            events_to_return.add(event)
    return events_to_return


def add_record_to_job_table(
    image_tag: str, event_names: list, request_schema: dict, expiration_days: int
) -> None:
    events_found_in_db = get_event_names_from_db(event_names)
    events_to_connect = [event.event_name for event in events_found_in_db]
    add_entry(
        Jobs(
            image_tag,
            request_schema,
            events_to_connect,
            expiration_days,
        ),
        db,
    )


def add_record_to_job_in_event_table(image_tag: str, event_names: list) -> None:
    job = Jobs.query.filter_by(image_tag=image_tag).first()
    event_names_found_in_db = get_events_from_db_per_event_names(set(event_names))
    for event in event_names_found_in_db:
        add_entry(JobsInEvents(job, event), db)


def get_job_parameters(request_body: dict) -> tuple:
    image_tag = request_body.get("image_tag")
    event_names = request_body.get("event_names")
    request_schema = request_body.get("request_schema")
    expiration_days = request_body.get("expiration_days")

    return image_tag, event_names, request_schema, expiration_days


def configure_new_job_response(request_body: dict) -> Response:
    validation_response = validate_request_parameters(
        JobConfigurationRequest, request_body
    )
    if validation_response and validation_response.status_code != HTTPStatus.OK:
        return validation_response

    validation_response = response_notes(request_body)

    image_tag, event_names, request_schema, expiration_days = get_job_parameters(
        request_body
    )

    add_record_to_job_table(image_tag, event_names, request_schema, expiration_days)
    add_record_to_job_in_event_table(image_tag, event_names)

    return make_response(
        f"{Endpoint.CONFIGURE_NEW_JOB.value[1:]} finished successfully. "
        f"{validation_response.get_data().decode('utf-8')}",
        HTTPStatus.OK,
    )
