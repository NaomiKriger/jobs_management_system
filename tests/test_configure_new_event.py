from http.client import BAD_REQUEST, OK

from consts import Endpoint
from tests.mocks import basic_schema_mock


def test_valid_input(test_client):
    data = {
        "event_name": "my_event",
        "schema": basic_schema_mock,
    }
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response.status_code == OK
    assert response.text == f"event {data.get('event_name')} added to the DB"


def test_missing_parameter(test_client):
    # missing event_name parameter
    data = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
        "required": ["name", "age"],
    }
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == "missing required parameter: event_name"

    # missing schema parameter
    response = test_client.post(
        Endpoint.CONFIGURE_NEW_EVENT.value, json={"event_name": "my_event"}
    )
    assert response.status_code == BAD_REQUEST
    assert response.text == "missing required parameter: schema"


def test_invalid_parameter_type(test_client):
    # event_name is not a string
    data = {
        "event_name": 123,
        "schema": basic_schema_mock,
    }
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == "event_name should be a string"

    # schema is not a json
    data = {"event_name": "my_event", "schema": "hey there"}
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == "schema should be a json"


def test_event_name_already_exists_in_db(test_client):
    data = {
        "event_name": "my_event",
        "schema": basic_schema_mock,
    }
    test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == f"event {data.get('event_name')} already exists"
