from enum import Enum


class Endpoint(Enum):
    CONFIGURE_NEW_EVENT = "/configure_new_event"
    CONFIGURE_NEW_JOB = "/configure_new_job"
    EXECUTE_JOB_BY_IMAGE_TAG = "/execute_job_by_image_tag"
    EXECUTE_JOB_BY_IMAGE_TAG_BATCH = "/execute_job_by_image_tag_batch"
    EXECUTE_JOBS_BY_EVENT = "/execute_jobs_by_event"
    VIEW_EVENT_INFO = "/view_event_info"
    VIEW_JOB_INFO = "/view_job_info"
