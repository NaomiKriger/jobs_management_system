from flask import Blueprint, Response, make_response, request

from src.consts import Endpoint
from src.endpoints.configure_new_event import configure_new_event_response
from src.endpoints.configure_new_job import configure_new_job_response
from src.endpoints.execute_job_by_image_tag import \
    execute_job_by_image_tag_response
from src.endpoints.execute_jobs_by_event import execute_jobs_by_event_response

views = Blueprint("views", __name__)


@views.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@views.route(Endpoint.CONFIGURE_NEW_EVENT.value, methods=["POST"])
def configure_new_event() -> Response:
    return configure_new_event_response(request.json)


@views.route(Endpoint.CONFIGURE_NEW_JOB.value, methods=["POST"])
def configure_new_job() -> Response:
    return configure_new_job_response(request.json)


@views.route(Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, methods=["POST"])
def execute_job_by_image_tag() -> Response:
    return execute_job_by_image_tag_response(request.json)


@views.route(Endpoint.EXECUTE_JOB_BY_IMAGE_TAG_BATCH.value, methods=["POST"])
def execute_job_by_image_tag_batch() -> Response:
    return make_response(f"{execute_job_by_image_tag_batch.__name__} is executed")


@views.route(Endpoint.EXECUTE_JOBS_BY_EVENT.value, methods=["POST"])
def execute_jobs_by_event() -> Response:
    return execute_jobs_by_event_response(request.json)


@views.route(Endpoint.VIEW_EVENT_INFO.value, methods=["GET"])
def view_event_info() -> Response:
    return make_response(f"{view_event_info.__name__} is executed")


@views.route(Endpoint.VIEW_JOB_INFO.value, methods=["GET"])
def view_job_info() -> Response:
    return make_response(f"{view_job_info.__name__} is executed")
