from http import HTTPStatus
from typing import List, Optional

from flask import Response, make_response, request
from pydantic import (BaseModel, Field, ValidationError, root_validator,
                      validator)
from pydantic.utils import to_camel

from consts import Endpoint
from database import add_entry, db, read_table
from models.event import Event
from models.job import Job
from models.job_in_event import JobInEvent

MAP_TYPES_TO_NAMES = {str: "string", int: "integer", list: "list", dict: "json"}


def get_event_names_from_db(event_names):
    return Event.query.filter(Event.event_name.in_(event_names)).all()


class JobConfigurationRequest(BaseModel):
    image_tag: str
    event_names: List[str]
    request_schema: dict = Field(..., alias="schema")
    expiration_days: int

    @root_validator(pre=True)
    def validate_not_empty(cls, values):
        for field_name, field_value in values.items():
            if field_name != "schema" and not field_value and field_value != 0:
                raise ValueError(f"{field_name} cannot be empty")
        return values

    @validator("request_schema", pre=True)
    def validate_schema_is_a_json(cls, schema):
        if not isinstance(schema, dict):
            raise ValueError("input should be a json")
        return schema

    @validator("event_names", pre=True)
    def validate_event_names_is_list_of_strings(cls, event_names):
        for event_name in event_names:
            if not isinstance(event_name, str):
                raise ValueError("input should be a list of strings")
        return event_names

    @validator("*", pre=True)
    def validate_input_types(cls, value, field):
        expected_type = field.type_
        if field.name == "event_names":
            return value
        if not isinstance(value, expected_type):
            raise ValueError(
                f"Expected type {MAP_TYPES_TO_NAMES.get(expected_type)} for field {field.name}, "
                f"but got {MAP_TYPES_TO_NAMES.get(type(value))} instead."
            )
        return value

    @validator("image_tag")
    def validate_image_tag_already_exists(cls, image_tag):
        image_tags = {job.image_tag for job in read_table(Job)}
        if image_tag in image_tags:
            raise ValueError(f"image {image_tag} already exists")
        return image_tag

    @validator("event_names")
    def validate_event_names_in_db(cls, event_names):
        event_names_found_in_db = get_event_names_from_db(event_names)
        if not event_names_found_in_db:
            raise ValueError("None of the provided event names was found in DB")

    @validator("expiration_days")
    def validate_expiration_days_greater_than_zero(cls, expiration_days):
        if expiration_days <= 0:
            raise ValueError(
                f"Expiration days should be greater than or equal to 1. "
                f"Expiration days value = {expiration_days}"
            )
        return expiration_days

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        alias_generator = to_camel


def get_input_event_names_that_are_not_found_in_db():
    input_event_names = request.json["event_names"]
    input_event_names_found_in_db = get_event_names_from_db(input_event_names)
    input_events_that_are_not_in_db = set(input_event_names) - set(
        event.event_name for event in input_event_names_found_in_db
    )
    return input_events_that_are_not_in_db


class ConfigureJobValidations:
    @staticmethod
    def validate_job_parameters() -> Optional[Response]:
        try:
            JobConfigurationRequest.parse_obj(request.json)
        except ValidationError as e:
            error_message = ""
            # error['loc'][-1] is the field's name
            for error in e.errors():
                prefix = (
                    f"{error['loc'][-1]}: " if error["loc"][-1] != "__root__" else ""
                )
                error_message = ", ".join(
                    [f"{prefix}" f"{error['msg']}" for error in e.errors()]
                )
            return make_response(error_message, HTTPStatus.BAD_REQUEST)

        notes = []
        input_events_that_are_not_found_in_db = (
            get_input_event_names_that_are_not_found_in_db()
        )
        if input_events_that_are_not_found_in_db:
            notes.append(
                f"the following event names were not found in DB and therefore "
                f"the job wasn't connected to them: {list(input_events_that_are_not_found_in_db)}"
            )
        return make_response(f"Job configured. Notes:{notes}", HTTPStatus.OK)


def get_events_from_db_per_event_names(event_names: set) -> set:
    events = read_table(Event)
    events_to_return = set()
    for event in events:
        if event.event_name in event_names:
            events_to_return.add(event)
    return events_to_return


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
    event_names_found_in_db = get_events_from_db_per_event_names(
        request.json["event_names"]
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
