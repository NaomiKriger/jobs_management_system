import os
import subprocess
from typing import List

from flask import Response, make_response, request

from src.aws_operations import ecr_login


def get_execution_command() -> List[str]:
    ecr_path = os.getenv("ECR_PATH")
    repository_name = os.getenv("ECR_REPOSITORY_NAME")
    image_tag = request.json.get("image_tag")
    executable_file_name = request.json.get("executable_file_name")

    cmd = [
        "docker",
        "run",
        f"{ecr_path}/{repository_name}:{image_tag}",
        "python",
        f"{executable_file_name}",
    ]
    cmd += get_execution_flags()

    return cmd


def get_execution_flags() -> list:
    flags = []
    execution_parameters = request.json.get("execution_parameters")
    for key, value in execution_parameters.items():
        flags.append(f"--{key}")
        flags.append(str(value))
    return flags


def execute_job_by_image_tag_response() -> Response:
    ecr_login()
    result = subprocess.run(
        get_execution_command(),
        capture_output=True,
        text=True,
    )

    return make_response({"output": result.stdout, "error": result.stderr})
