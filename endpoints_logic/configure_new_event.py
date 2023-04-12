from http.client import BAD_REQUEST, OK
from typing import Optional

from flask import Response, make_response, request

from database import add_entry, db, read_table
from models.event import Event


def validate_configure_new_event() -> Optional[Response]:
    try:
        event_name = request.json["event_name"]
        schema = request.json["schema"]
    except KeyError as e:
        return make_response(f"missing required parameter: {e.args[0]}", BAD_REQUEST)

    if not isinstance(event_name, str):
        return make_response("event_name should be a string", BAD_REQUEST)
    if not isinstance(schema, dict):
        return make_response("schema should be a json", BAD_REQUEST)

    event_names = {event.event_name for event in read_table(Event)}
    if event_name in event_names:
        return make_response(f"event {event_name} already exists", BAD_REQUEST)


def configure_new_event_response():
    validation_response = validate_configure_new_event()
    if validation_response:
        return validation_response

    event_name = request.json["event_name"]
    add_entry(Event(event_name, request.json["schema"]), db)

    return make_response(f"event {event_name} added to the DB", OK)
