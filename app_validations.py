from http.client import BAD_REQUEST
from typing import Optional

from flask import Response, make_response, request

from database import read_table

MAP_TYPES_TO_NAMES = {str: "string", int: "integer", list: "list", dict: "json"}


# TODO: could probably be validated with JSON schemas


def validate_input_type(
    param_name: str, param_value, param_expected_type
) -> Optional[Response]:
    if not isinstance(param_value, param_expected_type):
        return make_response(
            f"{param_name} type should be a {MAP_TYPES_TO_NAMES[param_expected_type]}. "
            f"{param_name} provided is {param_value}",
            BAD_REQUEST,
        )


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

    event_names = {event.event_name for event in read_table(event_model)}
    if event_name in event_names:
        return make_response(f"event {event_name} already exists", BAD_REQUEST)


class UploadJobValidations:
    @staticmethod
    def validate_empty_parameter(params: dict) -> Optional[Response]:
        empty_arguments = []
        for key, value in params.items():
            if not value["value"]:
                empty_arguments.append(key)
        if empty_arguments:
            return make_response(
                f"some required parameters are missing: {empty_arguments}", BAD_REQUEST
            )

    @staticmethod
    def validate_event_names(event_names: list) -> Optional[Response]:
        if not isinstance(event_names, list):
            return make_response(
                f"event_names type should be a list. event_names provided is {event_names}",
                BAD_REQUEST,
            )

    @staticmethod
    def get_event_names_found_in_db(event_model, event_names: list) -> set:
        event_names_in_db = {event.event_name for event in read_table(event_model)}
        event_names_found = set()
        for event_name in event_names:
            if event_name in event_names_in_db:
                event_names_found.add(event_name)
        return event_names_found

    @staticmethod
    def validate_upload_job(event_model) -> Optional[Response]:
        params = {}
        try:
            params["job_name"] = {"value": request.json["job_name"], "type": str}
            params["event_names"] = {"value": request.json["event_names"], "type": list}
            params["schema"] = {"value": request.json["schema"], "type": dict}
            params["job_logic"] = {
                "value": request.json["job_logic"],
                "type": str,  # TEMP - Docker image
            }
            params["expiration_days"] = {
                "value": request.json["expiration_days"],
                "type": int,
            }
        except KeyError as e:
            return make_response(
                f"missing required parameter: {e.args[0]}", BAD_REQUEST
            )

        empty_parameter_validation_response = (
            UploadJobValidations.validate_empty_parameter(params)
        )
        if empty_parameter_validation_response:
            return empty_parameter_validation_response

        for param_name in params.keys():
            response = validate_input_type(
                param_name, params[param_name]["value"], params[param_name]["type"]
            )
            if response:
                return response

        event_names_found_in_db = UploadJobValidations.get_event_names_found_in_db(
            event_model, params["event_names"]["value"]
        )
        if not event_names_found_in_db:
            return make_response(
                "Non of the provided event names was found in DB", BAD_REQUEST
            )
        else:
            events_not_in_db = (
                set(params["event_names"]["value"]) - event_names_found_in_db
            )
            notes = []
        if events_not_in_db:
            notes.append(
                f"the following event names were not found in DB and therefore "
                f"the job wasn't connected to them: {events_not_in_db}"
            )
        return make_response(f"Job uploaded. Notes:{notes}")
