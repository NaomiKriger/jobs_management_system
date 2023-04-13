from http import HTTPStatus
from typing import Optional

from flask import Response, make_response, request

from consts import Endpoint
from database import add_entry, db, read_table
from models.event import Event
from models.job import Job
from models.job_in_event import JobInEvent

MAP_TYPES_TO_NAMES = {str: "string", int: "integer", list: "list", dict: "json"}


def validate_input_type(
    param_name: str, param_value, param_expected_type
) -> Optional[Response]:
    if not isinstance(param_value, param_expected_type):
        return make_response(
            f"{param_name} type should be {MAP_TYPES_TO_NAMES[param_expected_type]}. "
            f"{param_name} provided is {param_value}",
            HTTPStatus.BAD_REQUEST,
        )


class ConfigureJobValidations:
    @staticmethod
    def validate_missing_parameter(params: dict) -> Optional[Response]:
        empty_arguments = []
        for param_name, param_attribute in params.items():
            if not param_attribute["value"] and param_attribute["value"] != 0:
                empty_arguments.append(param_name)
        if empty_arguments:
            return make_response(
                f"some required parameters are missing: {empty_arguments}",
                HTTPStatus.BAD_REQUEST,
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
    def _pull_parameters_if_not_missing(params) -> Optional[Response]:
        param_to_type = [
            ("image_tag", str),
            ("event_names", list),
            ("schema", dict),
            ("expiration_days", int),
        ]
        try:
            for param_name, param_type in param_to_type:
                params[param_name] = {
                    "value": request.json[param_name],
                    "type": param_type,
                }
        except KeyError as e:
            return make_response(
                f"missing required parameter: {e.args[0]}", HTTPStatus.BAD_REQUEST
            )

    @staticmethod
    def validate_job_parameters() -> Optional[Response]:
        params = {}
        params_pull_response = ConfigureJobValidations._pull_parameters_if_not_missing(
            params
        )
        if isinstance(params_pull_response, Response):
            return params_pull_response

        params_excluding_schema = params.copy()
        params_excluding_schema.pop("schema")
        empty_parameter_validation_response = (
            ConfigureJobValidations.validate_missing_parameter(params_excluding_schema)
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
            return make_response(
                f"Expiration days should be greater than or equal to 1. "
                f"Expiration days value = {params['expiration_days']['value']}",
                HTTPStatus.BAD_REQUEST,
            )

        image_tag_already_exists = Job.query.filter_by(
            image_tag=params["image_tag"]["value"]
        ).first()

        if image_tag_already_exists:
            return make_response(
                f"Image tag {params['image_tag']['value']} already exists",
                HTTPStatus.BAD_REQUEST,
            )

        event_names_found_in_db = Event.query.filter(
            Event.event_name.in_(params["event_names"]["value"])
        ).all()
        if not event_names_found_in_db:
            return make_response(
                "Non of the provided event names was found in DB",
                HTTPStatus.BAD_REQUEST,
            )

        events_not_in_db = set(params["event_names"]["value"]) - set(
            event.event_name for event in event_names_found_in_db
        )
        notes = []
        if events_not_in_db:
            notes.append(
                f"the following event names were not found in DB and therefore "
                f"the job wasn't connected to them: {list(events_not_in_db)}"
            )
        return make_response(f"Job configured. Notes:{notes}", HTTPStatus.OK)


def add_record_to_job_table():
    events_found_in_db = Event.query.filter(
        Event.event_name.in_(request.json["event_names"])
    ).all()
    events_to_connect = [event.event_name for event in events_found_in_db]
    add_entry(
        Job(
            request.json["image_tag"],
            request.json["schema"],
            events_to_connect,
            request.json["expiration_days"],
        ),
        db,
    )


def add_record_to_job_in_event_table():
    job = Job.query.filter_by(image_tag=request.json["image_tag"]).first()
    event_names_found_in_db = (
        ConfigureJobValidations.get_events_from_db_per_event_names(
            request.json["event_names"]
        )
    )
    for event in event_names_found_in_db:
        add_entry(JobInEvent(job, event), db)


def configure_new_job_response():
    validation_response = ConfigureJobValidations.validate_job_parameters()
    if validation_response.status_code != HTTPStatus.OK:
        return validation_response

    add_record_to_job_table()
    add_record_to_job_in_event_table()

    return make_response(
        f"{Endpoint.CONFIGURE_NEW_JOB.value[1:]} finished successfully. "
        f"{validation_response.get_data().decode('utf-8')}",
        HTTPStatus.OK,
    )
