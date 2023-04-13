from http.client import BAD_REQUEST, OK

from consts import Endpoint
from models.event import Event
from tests.mocks import basic_schema_mock


def test_valid_input(test_client):
    data = {
        "event_name": "test_event_1",
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
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                "required": ["name", "age"],
            }
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "EventName: field required"

    def test_empty_event_name(self, test_client):
        data = {
            "event_name": "",
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                "required": ["name", "age"],
            },
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "EventName: input cannot be empty"

    def test_empty_schema(self, test_client):
        data = {"event_name": "test_event_2", "schema": {}}
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == OK

    def test_missing_schema(self, test_client):
        response = test_client.post(
            Endpoint.CONFIGURE_NEW_EVENT.value, json={"event_name": "test_event_3"}
        )
        assert response.status_code == BAD_REQUEST
        assert response.text == "schema: field required"


class TestInvalidParameterType:
    def test_event_name_non_string_input_provided(self, test_client):
        data = {
            "event_name": 123,
            "schema": basic_schema_mock,
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert (
            response.status_code == OK
        )  # event_name is automatically cast to string by Pydantic

    def test_schema_is_not_a_json(self, test_client):
        data = {"event_name": "test_event_4", "schema": "hey there"}
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == BAD_REQUEST
        assert response.text == "schema: input should be a json"


def test_event_name_already_exists_in_db(test_client):
    data = {
        "event_name": "test_event_5",
        "schema": basic_schema_mock,
    }
    response_first = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    response_second = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response_first.status_code == OK
    assert response_first.text == f"event {data['event_name']} added to the DB"
    assert response_second.status_code == BAD_REQUEST
    assert (
        response_second.text
        == f"EventName: event {data.get('event_name')} already exists"
    )
