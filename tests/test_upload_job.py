import unittest
from http.client import BAD_REQUEST

from consts import Endpoint

# TODO: create a base_data json, which will be modified per test scenario (yet not modified globally)
from tests.mocks import basic_schema_mock


@unittest.skip("Not implemented")
def test_valid_input(test_client):
    """
    expected result: response.status_code == OK, new record added to job table, new record added to job_in_event table
    """
    pass


class TestInvalidJobName:
    """
    scenarios left to implement: job_name already exists
    """

    data = {
        "job_name": "my_job",
        "event_names": ["event_1", "event_2"],
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


class TestInvalidEventNames:
    """
    scenarios left to implement: event names in list are not strings
    """

    data = {
        "job_name": "my_job",
        "event_names": ["event_1", "event_2"],
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
        self.data["event_names"] = ["event_1", "event_2"]

    def test_non_of_event_names_is_found_in_db(self, test_client):
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "Non of the provided event names was found in DB"

    def test_at_least_one_of_event_names_is_not_found_in_db(self, test_client):
        self.data["event_names"] = ["test_event_1", "test_event_2"]
        response = test_client.post(Endpoint.UPLOAD_JOB.value, json=self.data)
        assert (
            response.data
            == b'{"message":"upload_job finished successfully. Job uploaded. Notes:[\\"the following event names were not found in DB and therefore the job wasn\'t connected to them: {\'test_event_2\'}\\"]"}\n'
        )


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


@unittest.skip("Not implemented")
def test_add_new_job_record_to_database(test_client):
    """
    scenarios: expiration days is not a non-negative integer
    """
    pass
