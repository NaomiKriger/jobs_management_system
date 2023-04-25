from typing import Optional

from pydantic import BaseModel, Field, validator
from pydantic.utils import to_camel

from src.models.events import Events


class EventConfigurationRequest(BaseModel):
    event_name: str = Field(..., min_length=1)
    request_schema: dict = Field(..., alias="schema")

    @validator("event_name")
    def validate_event_name_already_exists(cls, event_name: str) -> Optional[str]:
        event_names = {event.event_name for event in Events.query.all()}
        if event_name in event_names:
            raise ValueError(f"event {event_name} already exists")
        return event_name

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        alias_generator = to_camel
