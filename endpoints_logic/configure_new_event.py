from http import HTTPStatus
from typing import Optional

from flask import Response, make_response, request
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.utils import to_camel

from database import add_entry, db, read_table
from models.event import Event


class EventRequest(BaseModel):
    event_name: str
    request_schema: dict = Field(..., alias="schema")

    @validator("event_name")
    def validate_event_name_is_not_empty(cls, event_name):
        if not event_name:
            raise ValueError("input cannot be empty")
        return event_name

    @validator("event_name")
    def validate_event_name_already_exists(cls, event_name):
        event_names = {event.event_name for event in read_table(Event)}
        if event_name in event_names:
            raise ValueError(f"event {event_name} already exists")
        return event_name

    @validator("request_schema", pre=True)
    def validate_schema_is_a_json(cls, schema):
        if not isinstance(schema, dict):
            raise ValueError("input should be a json")
        return schema

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        alias_generator = to_camel


def validate_configure_new_event() -> Optional[Response]:
    try:
        EventRequest.parse_obj(request.json)
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
