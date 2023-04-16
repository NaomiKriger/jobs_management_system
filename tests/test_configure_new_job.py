import uuid
from http import HTTPStatus

from src.consts import Endpoint
from src.models.event import Event
from src.models.job import Job
from src.models.job_in_event import JobInEvent
from tests.conftest import event_name_pre_configured_in_db
from tests.mocks import basic_schema_mock

valid_request_body = {
    "image_tag": str(uuid.uuid4()),
    "event_names": [event_name_pre_configured_in_db],
    "schema": basic_schema_mock,
    "expiration_days": 365,
}


def test_valid_input(test_client):
    data = valid_request_body.copy()
    response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=data)
    job = Job.query.filter_by(image_tag=data["image_tag"]).first()
    job_in_event = JobInEvent.query.filter_by(job_id=job.id).first()
    event_id = (
        Event.query.filter_by(event_name=event_name_pre_configured_in_db).first().id
    )

    assert response.status_code == HTTPStatus.OK
    assert job is not None
    assert job.image_tag == data["image_tag"]
    assert job_in_event.event_id == event_id
    assert job_in_event.job_id == job.id
    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == "configure_new_job finished successfully. Job configured. Notes:[]"
    )


class TestImageTag:
    data = valid_request_body.copy()

    def test_empty_image_tag(self, test_client):
        self.data["image_tag"] = ""
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "image_tag cannot be empty"

    def test_image_tag_of_invalid_type(self, test_client):
        self.data["image_tag"] = 123
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.text
            == "ImageTag: Expected type string for field image_tag, but got integer instead."
        )

    def test_no_image_tag_parameter_provided(self, test_client):
        self.data.pop("image_tag")
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "ImageTag: field required"

    def test_image_tag_already_exists(self, test_client):
        self.data["image_tag"] = str(uuid.uuid4())
        response_first = test_client.post(
            Endpoint.CONFIGURE_NEW_JOB.value, json=self.data
        )
        response_second = test_client.post(
            Endpoint.CONFIGURE_NEW_JOB.value, json=self.data
        )
        assert response_first.status_code == HTTPStatus.OK
        assert response_second.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response_second.text
            == f"ImageTag: image {self.data['image_tag']} already exists"
        )


class TestEventNames:
    data = valid_request_body.copy()

    def test_empty_event_names(self, test_client):
        self.data["event_names"] = []
        self.data["image_tag"] = str(uuid.uuid4())
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "event_names cannot be empty"

    def test_event_names_type_is_invalid(self, test_client):
        self.data["event_names"] = [123]
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "EventNames: input should be a list of strings"

    def test_event_names_is_list_of_non_str_types(self, test_client):
        self.data["event_names"] = ["abc", 123]
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "EventNames: input should be a list of strings"

    def test_no_event_names(self, test_client):
        self.data.pop("event_names")
        self.data["image_tag"] = str(uuid.uuid4())
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "EventNames: field required"

    def test_none_of_event_names_is_found_in_db(self, test_client):
        self.data["image_tag"] = str(uuid.uuid4())
        self.data["event_names"] = [str(uuid.uuid4()), str(uuid.uuid4())]
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.text
            == "EventNames: None of the provided event names was found in DB"
        )

    def test_one_event_found_in_db_and_one_event_is_not_found(self, test_client):
        self.data["image_tag"] = str(uuid.uuid4())
        event_not_in_db = str(uuid.uuid4())
        self.data["event_names"] = [event_not_in_db, event_name_pre_configured_in_db]
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        job = Job.query.filter_by(image_tag=self.data["image_tag"]).first()
        job_in_event = JobInEvent.query.filter_by(job_id=job.id).first()
        event_id = (
            Event.query.filter_by(event_name=event_name_pre_configured_in_db).first().id
        )

        assert response.text == (
            'configure_new_job finished successfully. Job configured. Notes:["the following event '
            "names were not found in DB and therefore the job wasn't connected to them: "
            f"['{event_not_in_db}']\"]"
        )
        assert job is not None
        assert job_in_event.event_id == event_id
        assert job_in_event.job_id == job.id
        assert response.status_code == HTTPStatus.OK
        assert len(job.event_names) == 1


class TestSchema:
    """
    scenarios left to implement: schema is not a sub-type of one of the events' schemas
    """

    data = {
        "image_tag": str(uuid.uuid4()),
        "event_names": [event_name_pre_configured_in_db],
        "schema": basic_schema_mock,
        "expiration_days": 365,
    }

    def test_empty_schema(self, test_client):
        # it is acceptable to provide an empty schema
        self.data["image_tag"] = str(uuid.uuid4())
        self.data["schema"] = {}
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.OK

    def test_schema_is_not_a_json(self, test_client):
        self.data["image_tag"] = str(uuid.uuid4())
        self.data["schema"] = "abc"
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "schema: input should be a json"


class TestExpirationDays:
    data = valid_request_body.copy()

    def test_expiration_days_not_an_integer(self, test_client):
        self.data["image_tag"] = str(uuid.uuid4())
        self.data["expiration_days"] = "three days"
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.text == "ExpirationDays: "
            "Expected type integer for field expiration_days, but got string instead."
        )

    def test_expiration_days_not_greater_than_zero(self, test_client):
        self.data["expiration_days"] = 0
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.text
            == "ExpirationDays: Expiration days should be greater than or equal to 1. "
            f"Expiration days value = {self.data.get('expiration_days')}"
        )

    def test_expiration_days_is_empty(self, test_client):
        self.data["expiration_days"] = ""
        self.data["image_tag"] = str(uuid.uuid4())
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "expiration_days cannot be empty"

    def test_expiration_days_parameter_not_provided(self, test_client):
        self.data.pop("expiration_days")
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "ExpirationDays: field required"
