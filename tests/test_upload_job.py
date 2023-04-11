import unittest
from http.client import BAD_REQUEST, OK

from consts import Endpoint
from models import Event, Job, JobInEvent
from tests.mocks import basic_schema_mock

valid_request_body = {
    "image_tag": "my_job",
    "event_names": ["test_event_1"],
    "schema": basic_schema_mock,
    "job_logic": "TBD",
    "expiration_days": 365,
}


def test_valid_input(test_client):
    data = valid_request_body.copy()
    response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=data)
    job = Job.query.filter_by(image_tag=data["image_tag"]).first()
    job_in_event = JobInEvent.query.filter_by(job_id=job.id).first()
    event_id = Event.query.filter_by(event_name="test_event_1").first().id

    assert response.status_code == OK
    assert job is not None
    assert job.image_tag == data["image_tag"]
    assert job_in_event.event_id == event_id
    assert job_in_event.job_id == job.id
    assert response.status_code == OK
    assert response.text == "configure_new_job finished successfully. Job configured. Notes:[]"


class TestInvalidImageTag:
    data = valid_request_body.copy()

    def test_missing_image_tag(self, test_client):
        self.data["image_tag"] = ""
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == f"some required parameters are missing: ['image_tag']"

    def test_image_tag_of_invalid_type(self, test_client):
        self.data["image_tag"] = 123
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
                response.text
                == f"image_tag type should be string. image_tag provided is {self.data.get('image_tag')}"
        )

    def test_no_image_tag_parameter_provided(self, test_client):
        self.data.pop("image_tag")
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: image_tag"
        self.data["image_tag"] = "my_job"

    def test_image_tag_already_exists(self, test_client):
        self.data["image_tag"] = "test_job_1"
        response_first = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        response_second = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response_first.status_code == OK
        assert response_second.status_code == BAD_REQUEST
        assert (
                response_second.text == f"Image tag {self.data['image_tag']} already exists"
        )


class TestInvalidEventNames:
    """
    scenarios left to implement: event names in list are not strings
    """

    data = valid_request_body.copy()

    def test_empty_event_names(self, test_client):
        self.data["event_names"] = []
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == f"some required parameters are missing: ['event_names']"

    def test_event_names_type_is_invalid(self, test_client):
        self.data["event_names"] = 123
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
                response.text
                == f"event_names type should be list. event_names provided is {self.data.get('event_names')}"
        )

    def test_no_event_names(self, test_client):
        self.data.pop("event_names")
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: event_names"

    def test_none_of_event_names_is_found_in_db(self, test_client):
        self.data["image_tag"] = "test_job_2"
        self.data["event_names"] = ["event_123", "event_345"]
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "Non of the provided event names was found in DB"

    def test_one_event_found_in_db_and_one_event_is_not_found(self, test_client):
        self.data[
            "image_tag"
        ] = "test_job_2"  # test_event_1 pre-configured in DB in conftest.py
        self.data["event_names"] = ["test_event_1", "test_event_2"]
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        job = Job.query.filter_by(image_tag=self.data["image_tag"]).first()
        job_in_event = JobInEvent.query.filter_by(job_id=job.id).first()
        event_id = Event.query.filter_by(event_name="test_event_1").first().id

        assert response.text == (
            'configure_new_job finished successfully. Job configured. Notes:["the following event '
            "names were not found in DB and therefore the job wasn't connected to them: "
            "{'test_event_2'}\"]"
        )
        assert job is not None
        assert job_in_event.event_id == event_id
        assert job_in_event.job_id == job.id
        assert response.status_code == OK


class TestInvalidSchema:
    """
    scenarios: schema is not a sub-type of one of the events' schemas
    """

    data = {
        "image_tag": "test_job_3",
        "event_names": ["test_event_1"],
        "schema": basic_schema_mock,
        "job_logic": "TBD",
        "expiration_days": 365,
    }

    def test_schema_is_not_a_json(self, test_client):
        self.data["schema"] = "abc"
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
                response.text == f"schema type should be json. "
                                 f"schema provided is {self.data.get('schema')}"
        )

    # it is acceptable to provide an empty schema
    def test_empty_schema(self, test_client):
        self.data["schema"] = {}
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == OK


@unittest.skip("Not implemented")
def test_invalid_job_type(test_client):
    """
    scenarios: job is not a Docker image
    """
    pass


class TestInvalidExpirationDays:
    data = valid_request_body.copy()

    def test_expiration_days_not_an_integer(self, test_client):
        self.data["expiration_days"] = "a"
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
                response.text == f"expiration_days type should be integer. "
                                 f"expiration_days provided is {self.data.get('expiration_days')}"
        )

    def test_expiration_days_not_greater_than_zero(self, test_client):
        self.data["expiration_days"] = 0
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
                response.text == f"Expiration days should be greater than or equal to 1. "
                                 f"Expiration days value = {self.data.get('expiration_days')}"
        )

    def test_expiration_days_is_empty(self, test_client):
        self.data["expiration_days"] = ""
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
                response.text == "some required parameters are missing: ['expiration_days']"
        )

    def test_expiration_days_parameter_not_provided(self, test_client):
        self.data.pop("expiration_days")
        response = test_client.post(Endpoint.CONFIGURE_NEW_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: expiration_days"
