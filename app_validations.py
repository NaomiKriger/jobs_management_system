from http.client import BAD_REQUEST
from typing import Optional

from flask import Response, make_response, request

from database import read_table


def configure_new_event_validations(event_model) -> Optional[Response]:
    try:
        event_name = request.json["event_name"]
        schema = request.json["schema"]
    except KeyError as e:
        return make_response(f"missing required parameter: {e.args[0]}", BAD_REQUEST)

    if not isinstance(event_name, str):
        return make_response("event_name should be a string", BAD_REQUEST)
    if not isinstance(schema, dict):
        return make_response("schema should be a json", BAD_REQUEST)

    events = read_table(event_model)
    event_names = [event.event_name for event in events]
    if event_name in event_names:
        return make_response(f"event {event_name} already exists", BAD_REQUEST)
