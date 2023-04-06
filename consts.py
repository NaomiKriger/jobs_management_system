from enum import Enum


class Endpoint(Enum):
    CONFIGURE_NEW_EVENT = "/configure_new_event"
    UPLOAD_JOB = "/upload_job"
