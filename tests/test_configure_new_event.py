from http.client import BAD_REQUEST, OK

from consts import Endpoint
from models.event import Event
from tests.mocks import basic_schema_mock


def test_valid_input(test_client):
    data = {
        "event_name": "my_event",
        "schema": basic_schema_mock,
    }
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    event = Event.query.filter_by(event_name=data["event_name"]).first()
    assert response.status_code == OK
    assert response.text == f"event {data['event_name']} added to the DB"
    assert event is not None
    assert event.event_name == data["event_name"]
    assert event.schema == data["schema"]


class TestMissingParameter:
    def test_missing_event_name(self, test_client):
        data = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: event_name"

    def test_missing_schema(self, test_client):
        response = test_client.post(
            Endpoint.CONFIGURE_NEW_EVENT.value, json={"event_name": "my_event"}
        )
        assert response.status_code == BAD_REQUEST
        assert response.text == "missing required parameter: schema"


class TestInvalidParameterType:
    def test_event_name_is_not_a_string(self, test_client):
        data = {
            "event_name": 123,
            "schema": basic_schema_mock,
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "event_name should be a string"

    def test_schema_is_not_a_json(self, test_client):
        data = {"event_name": "my_event", "schema": "hey there"}
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "schema should be a json"


def test_event_name_already_exists_in_db(test_client):
    data = {
        "event_name": "test_event_in_db",
        "schema": basic_schema_mock,
    }
    response_first = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    response_second = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response_first.status_code == OK
    assert response_first.text == f"event {data['event_name']} added to the DB"
    assert response_second.status_code == BAD_REQUEST
    assert response_second.text == f"event {data.get('event_name')} already exists"
