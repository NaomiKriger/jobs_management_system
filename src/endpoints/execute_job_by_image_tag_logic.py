import os
import subprocess
from typing import List

from flask import Response, make_response

from src.aws_operations import ecr_login


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
    for key, value in execution_parameters.items():
        flags.append(f"--{key}")
        flags.append(str(value))
    return flags


def get_execute_job_parameters(request_body: dict) -> tuple:
    image_tag = request_body.get("image_tag")
    execution_parameters = request_body.get("execution_parameters")
    executable_file_name = request_body.get("executable_file_name")

    return image_tag, execution_parameters, executable_file_name


def execute_job_by_image_tag_response(request_body: dict) -> Response:
    image_tag, execution_parameters, executable_file_name = get_execute_job_parameters(
        request_body
    )

    ecr_login()
    result = subprocess.run(
        get_execution_command(image_tag, execution_parameters, executable_file_name),
        capture_output=True,
        text=True,
    )

    return make_response({"output": result.stdout, "error": result.stderr})
