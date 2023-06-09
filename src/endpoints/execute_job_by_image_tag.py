import os
import subprocess
from http import HTTPStatus
from typing import List

from flask import Response, make_response

from src.aws_operations import ecr_login
from src.endpoints.common import validate_request_parameters
from src.models.jobs import Jobs
from src.serializers.execute_job_by_image_tag import JobExecutionRequest


def get_execution_command(
    image_tag: str, execution_parameters: dict, executable_file_name: str
) -> List[str]:
    ecr_path = os.getenv("ECR_PATH")
    repository_name = os.getenv("ECR_REPOSITORY_NAME")

    cmd = [
        "docker",
        "run",
        f"{ecr_path}/{repository_name}:{image_tag}",
        "python",
        f"{executable_file_name}",
    ]
    cmd += get_execution_flags(execution_parameters)

    return cmd


def get_execution_flags(execution_parameters: dict) -> list:
    flags = []
    if execution_parameters:
        for key, value in execution_parameters.items():
            flags.append(f"--{key}")
            flags.append(str(value))
    return flags


def get_request_parameters(request_body: dict) -> tuple:
    image_tag = str(request_body.get("image_tag"))
    execution_parameters = request_body.get("execution_parameters")
    # TODO: remove executable_file_name field from now on the value is "main.py" for all jobs (prerequisite for users)
    executable_file_name = request_body.get("executable_file_name")

    return image_tag, execution_parameters, executable_file_name


def is_image_tag_in_db(image_tag: str) -> bool:
    return bool(Jobs.query.filter_by(image_tag=image_tag).first())


def execute_job_by_image_tag_response(request_body: dict) -> Response:
    validation_response = validate_request_parameters(JobExecutionRequest, request_body)
    if validation_response:
        return validation_response

    image_tag, execution_parameters, executable_file_name = get_request_parameters(
        request_body
    )

    if not is_image_tag_in_db(image_tag):
        return make_response(
            f"image_tag {image_tag} not found in DB", HTTPStatus.BAD_REQUEST
        )

    ecr_login()
    result = subprocess.run(
        get_execution_command(image_tag, execution_parameters, executable_file_name),
        capture_output=True,
        text=True,
    )

    return make_response({"output": result.stdout, "error": result.stderr})
