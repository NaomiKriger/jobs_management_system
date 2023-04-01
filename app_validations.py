from http.client import BAD_REQUEST

from flask import make_response, request


def configure_new_event_validations(events):
    try:
        event_name = request.json["event_name"]
        schema = request.json["schema"]
    except KeyError as e:
        return make_response(f"missing required parameter: {e.args[0]}", BAD_REQUEST)

    if not isinstance(event_name, str):
        return make_response("event_name should be a string", BAD_REQUEST)
    if not isinstance(schema, dict):
        return make_response("schema should be a json", BAD_REQUEST)

    if event_name in events:
        return make_response(f"event {event_name} already exists", BAD_REQUEST)
