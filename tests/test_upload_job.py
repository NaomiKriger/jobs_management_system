import unittest
from http.client import BAD_REQUEST, OK

from consts import Endpoint
# TODO: create a base_data json, which will be modified per test scenario (yet not modified globally)
from models import Event, Job, JobInEvent
from tests.mocks import basic_schema_mock


def test_valid_input(test_client):
    data = {
        "job_name": "my_job",
        "event_names": ["test_event_1"],
        "schema": basic_schema_mock,
        "job_logic": "TBD",
        "expiration_days": 365,
    }
    response = test_client.post(Endpoint.UPLOAD_JOB.value, json=data)
    job = Job.query.filter_by(job_name=data["job_name"]).first()
    job_in_event = JobInEvent.query.filter_by(job_id=job.id).first()
    event_id = Event.query.filter_by(event_name="test_event_1").first().id

    assert response.status_code == OK
    assert job is not None
    assert job.job_name == data["job_name"]
    assert job_in_event.event_id == event_id
    assert job_in_event.job_id == job.id
    assert response.status_code == OK
    assert response.text == "upload_job finished successfully. Job uploaded. Notes:[]"


class TestInvalidJobName:
    """
    scenarios left to implement: job_name already exists
    """

    data = {
        "job_name": "my_job",
        "event_names": ["test_event_1", "test_event_2"],
        "schema": basic_schema_mock,
        "job_logic": "TBD",
        "expiration_days": 365,
    }

    def test_missing_job_name(self, test_client):
        self.data["job_name"] = ""
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == f"some required parameters are missing: ['job_name']"

    def test_job_name_of_invalid_type(self, test_client):
        self.data["job_name"] = 123
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
            response.text
            == f"job_name type should be a string. job_name provided is {self.data.get('job_name')}"
        )

    def test_no_job_name_parameter_provided(self, test_client):
        self.data.pop("job_name")
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: job_name"
        self.data["job_name"] = "my_job"

    def test_job_name_already_exists(self, test_client):
        self.data["job_name"] = "test_job_1"
        response_first = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        response_second = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response_first.status_code == OK
        assert response_second.status_code == BAD_REQUEST
        assert response_second.text == f"Job name {self.data['job_name']} already exists"


class TestInvalidEventNames:
    """
    scenarios left to implement: event names in list are not strings
    """

    data = {
        "job_name": "my_job",
        "event_names": ["test_event_1", "test_event_1"],
        "schema": basic_schema_mock,
        "job_logic": "TBD",
        "expiration_days": 365,
    }

    def test_empty_event_names(self, test_client):
        self.data["event_names"] = []
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == f"some required parameters are missing: ['event_names']"

    def test_event_names_type_is_invalid(self, test_client):
        self.data["event_names"] = 123
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert (
            response.text
            == f"event_names type should be a list. event_names provided is {self.data.get('event_names')}"
        )

    def test_no_event_names(self, test_client):
        self.data.pop("event_names")
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: event_names"

    def test_none_of_event_names_is_found_in_db(self, test_client):
        self.data["job_name"] = "test_job_2"
        self.data["event_names"] = ["event_123", "event_345"]
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "Non of the provided event names was found in DB"

    def test_one_event_found_in_db_and_one_event_is_not_found(self, test_client):
        self.data["job_name"] = "test_job_2"   # test_event_1 pre-configured in DB in conftest.py
        self.data["event_names"] = ["test_event_1", "test_event_2"]
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        job = Job.query.filter_by(job_name=self.data["job_name"]).first()
        job_in_event = JobInEvent.query.filter_by(job_id=job.id).first()
        event_id = Event.query.filter_by(event_name="test_event_1").first().id

        assert response.text == (
            'upload_job finished successfully. Job uploaded. Notes:["the following event '
            "names were not found in DB and therefore the job wasn't connected to them: "
            "{'test_event_2'}\"]"
        )
        assert job is not None
        assert job_in_event.event_id == event_id
        assert job_in_event.job_id == job.id
        assert response.status_code == OK


@unittest.skip("Not implemented")
def test_invalid_schema(test_client):
    """
    scenarios: schema is not a json, schema is not a sub-type of one of the events' schemas
    """
    pass


@unittest.skip("Not implemented")
def test_invalid_job_type(test_client):
    """
    scenarios: job is not a Docker image
    """
    pass


@unittest.skip("Not implemented")
def test_invalid_expiration_days(test_client):
    """
    scenarios: expiration days is not a non-negative integer
    """
    pass
