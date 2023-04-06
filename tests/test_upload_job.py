import unittest
from http.client import BAD_REQUEST

from consts import Endpoint

# TODO: create a base_data json, which will be modified per test scenario (yet not modified globally)


@unittest.skip("Not implemented")
def test_valid_input(test_client):
    """
    expected result: response.status_code == OK, new record added to job table, new record added to job_in_event table
    """
    pass


def test_invalid_job_name(test_client):
    data = {
        "job_name": "my_job",
        "event_names": ["event_1", "event_2"],
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        },
        "job_logic": "TBD",
        "expiration_days": 365
    }

    """
    scenarios left to implement: job_name already exists
    """

    data["job_name"] = ""
    response = test_client.post(Endpoint.UPLOAD_JOB.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == f"some required parameters are missing: ['job_name']"

    data["job_name"] = 123
    response = test_client.post(Endpoint.UPLOAD_JOB.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == f"job_name type should be a string. job_name provided is {data.get('job_name')}"

    data.pop("job_name")
    response = test_client.post(Endpoint.UPLOAD_JOB.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == "missing required parameter: job_name"


@unittest.skip("Not implemented")
def test_invalid_event_names(test_client):
    """
    scenarios: event_names not a list, event names in list are not strings, event_names list is empty,
    at least one event name is not in DB, none of the event names is in DB
    """
    pass


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
