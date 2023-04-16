from http import HTTPStatus

from src.consts import Endpoint
from src.models.events import Events
from tests.mocks import basic_schema_mock


def test_valid_input(test_client):
    data = {
        "event_name": "test_event_1",
        "schema": basic_schema_mock,
    }
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    event = Events.query.filter_by(event_name=data["event_name"]).first()
    assert response.status_code == HTTPStatus.OK
    assert response.text == f"event {data['event_name']} added to the DB"
    assert event is not None
    assert event.event_name == data["event_name"]
    assert event.schema == data["schema"]


class TestEventName:
    def test_missing_event_name(self, test_client):
        data = {
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                "required": ["name", "age"],
            }
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
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
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "EventName: input cannot be empty"

    def test_event_name_input_is_not_a_string(self, test_client):
        # event_name is automatically cast to string by Pydantic
        data = {
            "event_name": 123,
            "schema": basic_schema_mock,
        }
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == HTTPStatus.OK

    def test_event_name_already_exists_in_db(self, test_client):
        data = {
            "event_name": "test_event_5",
            "schema": basic_schema_mock,
        }
        response_first = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        response_second = test_client.post(
            Endpoint.CONFIGURE_NEW_EVENT.value, json=data
        )
        assert response_first.status_code == HTTPStatus.OK
        assert response_first.text == f"event {data['event_name']} added to the DB"
        assert response_second.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response_second.text
            == f"EventName: event {data.get('event_name')} already exists"
        )


class TestSchema:
    def test_missing_schema(self, test_client):
        response = test_client.post(
            Endpoint.CONFIGURE_NEW_EVENT.value, json={"event_name": "test_event_3"}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "schema: field required"

    def test_empty_schema(self, test_client):
        # it is acceptable to provide an empty schema
        data = {"event_name": "test_event_2", "schema": {}}
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == HTTPStatus.OK

    def test_schema_of_invalid_type(self, test_client):
        data = {"event_name": "test_event_4", "schema": "hey there"}
        response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "schema: input should be a json"
