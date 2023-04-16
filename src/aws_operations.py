import os
from datetime import datetime

import boto3

DATETIME_FORMAT = "%m/%d/%Y, %H:%M:%S"


def ecr_login():
    token = os.environ.get("ECR_LOGIN_TOKEN")
    expiration_time = os.environ.get("ECR_LOGIN_TOKEN_EXPIRATION_TIME")
    if expiration_time:
        expiration_time = datetime.strptime(expiration_time, DATETIME_FORMAT)

    if (
        token and expiration_time and datetime.now() < expiration_time
    ):  # token is still valid
        return

    ecr_client = boto3.client("ecr")
    response = ecr_client.get_authorization_token()
    token = response["authorizationData"][0]["authorizationToken"]
    expiration_time = response["authorizationData"][0]["expiresAt"]

    # cache the token
    os.environ["ECR_LOGIN_TOKEN"] = token
    os.environ["ECR_LOGIN_TOKEN_EXPIRATION_TIME"] = expiration_time.strftime(
        DATETIME_FORMAT
    )
