from http import HTTPStatus
from typing import Optional

from flask import Response, make_response, request
from pydantic import ValidationError

from database import add_entry, db
from endpoints.configure_new_event_entity import EventConfigurationRequest
from models.event import Event


def validate_configure_new_event() -> Optional[Response]:
    try:
        EventConfigurationRequest.parse_obj(request.json)
    except ValidationError as e:
        # error['loc'][-1] is the field's name
        error_message = ", ".join(
            [f"{error['loc'][-1]}: {error['msg']}" for error in e.errors()]
        )
        return make_response(error_message, HTTPStatus.BAD_REQUEST)


def configure_new_event_response():
    validation_response = validate_configure_new_event()
    if validation_response:
        return validation_response

    event_name = request.json["event_name"]
    add_entry(Event(event_name, request.json["schema"]), db)

    return make_response(f"event {event_name} added to the DB", HTTPStatus.OK)
