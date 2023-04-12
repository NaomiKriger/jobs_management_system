from http.client import BAD_REQUEST, OK
from typing import Optional

from flask import Response, make_response, request

from database import read_table
from models.event import Event
from models.job import Job

MAP_TYPES_TO_NAMES = {str: "string", int: "integer", list: "list", dict: "json"}


# TODO: could probably be validated with JSON schemas


def validate_input_type(param_name: str, param_value, param_expected_type) -> Optional[Response]:
    if not isinstance(param_value, param_expected_type):
        return make_response(
            f"{param_name} type should be {MAP_TYPES_TO_NAMES[param_expected_type]}. "
            f"{param_name} provided is {param_value}",
            BAD_REQUEST,
        )


def configure_new_event_validations() -> Optional[Response]:
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


class ConfigureJobValidations:
    @staticmethod
    def validate_empty_parameter(params: dict) -> Optional[Response]:
        empty_arguments = []
        for param_name, param_attribute in params.items():
            if not param_attribute["value"] and param_attribute["value"] != 0:
                empty_arguments.append(param_name)
        if empty_arguments:
            return make_response(
                f"some required parameters are missing: {empty_arguments}", BAD_REQUEST
            )

    @staticmethod
    def get_events_from_db_per_event_names(event_names: set) -> set:
        events = read_table(Event)
        events_to_return = set()
        for event in events:
            if event.event_name in event_names:
                events_to_return.add(event)
        return events_to_return

    @staticmethod
    def pull_parameters_if_not_missing(params) -> Optional[Response]:
        param_to_type = [
            ("image_tag", str),
            ("event_names", list),
            ("schema", dict),
            ("expiration_days", int),
        ]
        try:
            for pair in param_to_type:
                params[pair[0]] = {"value": request.json[pair[0]], "type": pair[1]}
        except KeyError as e:
            return make_response(
                f"missing required parameter: {e.args[0]}", BAD_REQUEST
            )

    @staticmethod
    def validate_job_parameters() -> Optional[Response]:
        params = {}
        params_pull_response = ConfigureJobValidations.pull_parameters_if_not_missing(params)
        if isinstance(params_pull_response, Response):
            return params_pull_response

        params_excluding_schema = params.copy()
        params_excluding_schema.pop("schema")
        empty_parameter_validation_response = (
            ConfigureJobValidations.validate_empty_parameter(params_excluding_schema)
        )
        if empty_parameter_validation_response:
            return empty_parameter_validation_response

        for param_name in params.keys():
            input_type_validation_response = validate_input_type(
                param_name, params[param_name]["value"], params[param_name]["type"]
            )
            if input_type_validation_response:
                return input_type_validation_response
        if params["expiration_days"]["value"] <= 0:
            return make_response(f"Expiration days should be greater than or equal to 1. "
                                 f"Expiration days value = {params['expiration_days']['value']}", BAD_REQUEST)

        image_tag_already_exists = Job.query.filter_by(image_tag=params["image_tag"]["value"]).first()

        if image_tag_already_exists:
            return make_response(f"Image tag {params['image_tag']['value']} already exists", BAD_REQUEST)

        event_names_found_in_db = Event.query.filter(
            Event.event_name.in_(params["event_names"]["value"])).all()
        if not event_names_found_in_db:
            return make_response("Non of the provided event names was found in DB", BAD_REQUEST)

        events_not_in_db = set(params["event_names"]["value"]) - set(
            event.event_name for event in event_names_found_in_db)
        notes = []
        if events_not_in_db:
            notes.append(
                f"the following event names were not found in DB and therefore "
                f"the job wasn't connected to them: {list(events_not_in_db)}"
            )
        return make_response(f"Job configured. Notes:{notes}", OK)
