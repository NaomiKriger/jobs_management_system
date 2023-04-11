import os
import subprocess


def ecr_login():
    aws_region = os.getenv("AWS_REGION")
    ecr_repository = os.getenv("ECR_PATH") + "/" + os.getenv("ECR_REPOSITORY_NAME")

    aws_login_cmd = f"aws ecr get-login-password --region {aws_region}"
    ecr_login_cmd = f"docker login --username AWS --password-stdin {ecr_repository}"

    aws_login_output = subprocess.check_output(aws_login_cmd, shell=True)
    subprocess.check_call(
        f"echo {aws_login_output.decode()} | {ecr_login_cmd}", shell=True
    )
