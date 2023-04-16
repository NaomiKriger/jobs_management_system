from typing import Optional

from pydantic import BaseModel, Field, validator
from pydantic.utils import to_camel

from src.models.events import Events


class EventConfigurationRequest(BaseModel):
    event_name: str
    request_schema: dict = Field(..., alias="schema")

    @validator("event_name")
    def validate_event_name_is_not_empty(cls, event_name: str) -> Optional[str]:
        if not event_name:
            raise ValueError("input cannot be empty")
        return event_name

    @validator("event_name")
    def validate_event_name_already_exists(cls, event_name: str) -> Optional[str]:
        event_names = {event.event_name for event in Events.query.all()}
        if event_name in event_names:
            raise ValueError(f"event {event_name} already exists")
        return event_name

    @validator("request_schema", pre=True)
    def validate_schema_is_a_json(cls, schema: dict) -> Optional[dict]:
        if not isinstance(schema, dict):
            raise ValueError("input should be a json")
        return schema

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        alias_generator = to_camel
