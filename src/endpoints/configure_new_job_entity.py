from typing import List

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.utils import to_camel

from src.database import read_table
from src.endpoints.commons import get_event_names_from_db
from src.models.job import Job

MAP_TYPES_TO_NAMES = {str: "string", int: "integer", list: "list", dict: "json"}


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
