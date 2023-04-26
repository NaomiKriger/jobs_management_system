from http import HTTPStatus

from flask import Response, make_response

from src.endpoints.execute_job_by_image_tag import \
    execute_job_by_image_tag_response
from src.models.events import Events
from src.models.jobs_in_events import JobsInEvents


def get_request_parameters(request_body: dict) -> tuple:
    event_name = str(request_body.get("event_name"))
    request_data = str(request_body.get("request_data"))

    return event_name, request_data


def is_event_name_in_db(event_name: str) -> bool:
    return bool(Events.query.filter_by(event_name=event_name).first())


def get_image_tags_of_all_jobs_connected_to_event(event_name: str) -> list:
    event_id = Events.query.filter_by(event_name=event_name).first().id
    jobs_in_events = JobsInEvents.query.filter_by(event_id=event_id).all()
    return [job_in_event.job.image_tag for job_in_event in jobs_in_events]


def execute_jobs_by_event_response(request_body: dict) -> Response:
    # validation_response = validate_request_parameters(ExecuteJobsByEventRequest, request_body)
    # if validation_response:
    #     return validation_response

    event_name, request_data = get_request_parameters(request_body)

    if not is_event_name_in_db(event_name):
        return make_response(
            f"event_name {event_name} not found in DB", HTTPStatus.BAD_REQUEST
        )

    image_tags = get_image_tags_of_all_jobs_connected_to_event(event_name)

    responses = []
    for image_tag in image_tags:
        response = execute_job_by_image_tag_response(
            {
                "image_tag": image_tag,
                "execution_parameters": request_body["request_data"],
                "executable_file_name": "main.py",
            }
        )

        responses.append(
            {"image_tag": image_tag, "response": response.data.decode("utf-8")}
        )

    return make_response({"responses": responses})
