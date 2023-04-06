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


class UploadJobValidations:
    @staticmethod
    def validate_job_name(job_name: str) -> Optional[Response]:
        if not isinstance(job_name, str):
            return make_response(
                f"job_name type should be a string. job_name provided is {job_name}",
                BAD_REQUEST,
            )

    @staticmethod
    def validate_empty_parameter(params: dict) -> Optional[Response]:
        empty_arguments = []
        for key, value in params.items():
            if not value:
                empty_arguments.append(key)
        if empty_arguments:
            return make_response(
                f"some required parameters are missing: {empty_arguments}", BAD_REQUEST
            )

    @staticmethod
    def validate_upload_job(event_model) -> Optional[Response]:
        params = {}
        try:
            params["job_name"] = request.json["job_name"]
            params["event_names"] = request.json["event_names"]
            params["schema"] = request.json["schema"]
            params["job_logic"] = request.json["job_logic"]
            params["expiration_days"] = request.json["expiration_days"]
        except KeyError as e:
            return make_response(
                f"missing required parameter: {e.args[0]}", BAD_REQUEST
            )

        job_name_validation_response = UploadJobValidations.validate_job_name(
            params["job_name"]
        )
        if job_name_validation_response:
            return job_name_validation_response

        empty_parameter_validation_response = (
            UploadJobValidations.validate_empty_parameter(params)
        )
        if empty_parameter_validation_response:
            return empty_parameter_validation_response
