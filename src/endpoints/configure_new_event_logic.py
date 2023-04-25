from http import HTTPStatus

from flask import Response, make_response

from src.database import db
from src.endpoints.common import add_entry, validate_request_parameters
from src.endpoints.configure_new_event_entity import EventConfigurationRequest
from src.models.events import Events


def get_event_parameters(request_body: dict) -> tuple:
    event_name = request_body.get("event_name")
    schema = request_body.get("schema")

    return event_name, schema


def configure_new_event_response(request_body: dict) -> Response:
    validation_response = validate_request_parameters(EventConfigurationRequest, request_body)
    if validation_response:
        return validation_response

    event_name, schema = get_event_parameters(request_body)
    add_entry(Events(event_name, schema), db)

    return make_response(f"event {event_name} added to the DB", HTTPStatus.OK)
