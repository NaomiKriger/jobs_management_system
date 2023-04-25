from typing import Optional

from pydantic import BaseModel, validator
from pydantic.utils import to_camel


class JobExecutionRequest(BaseModel):
    image_tag: str
    execution_parameters: dict = {}
    executable_file_name: str

    @validator("image_tag")
    def validate_image_tag_is_not_empty(cls, image_tag: str) -> Optional[str]:
        if not image_tag:
            raise ValueError("input cannot be empty")
        return image_tag

    @validator("executable_file_name")
    def validate_executable_file_name_is_not_empty(
        cls, executable_file_name: str
    ) -> Optional[str]:
        if not executable_file_name:
            raise ValueError("input cannot be empty")
        return executable_file_name

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        alias_generator = to_camel
