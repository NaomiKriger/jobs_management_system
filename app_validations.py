from http.client import BAD_REQUEST
from typing import Optional

from flask import Response, make_response, request

from database import read_table


# TODO: could probably be validated with JSON schemas

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


def upload_job_validations(event_model) -> Optional[Response]:
    try:
        job_name = request.json["job_name"]
        event_names = request.json["event_names"]
        schema = request.json["schema"]
        job_logic = request.json["job_logic"]
        expiration_days = request.json["expiration_days"]
    except KeyError as e:
        return make_response(f"missing required parameter: {e.args[0]}", BAD_REQUEST)

    if not isinstance(job_name, str):
        return make_response(f"job_name type should be a string. job_name provided is {job_name}", BAD_REQUEST)

    empty_arguments = []
    for argument in ["job_name", "event_names", "schema", "job_logic", "expiration_days"]:
        if not eval(argument):
            empty_arguments.append(argument)
    if empty_arguments:
        return make_response(f"some required parameters are missing: {empty_arguments}", BAD_REQUEST)
