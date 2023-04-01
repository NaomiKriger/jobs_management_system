from http.client import BAD_REQUEST, OK
from unittest import TestCase

from app import app

"""
This file is obsolete since I didn't manage to use
flask app test client as fixture in unittest classes.
Switched to pytest methods instead.
"""


class TestIndex(TestCase):
    def test_index(self):
        with app.test_client() as test_client:
            response = test_client.get("/")
            assert response.status_code == OK
            json_response = response.get_json()
            assert json_response == {
                "message": "Welcome to the jobs management system!"
            }
            assert "Welcome to the jobs management system!" in response.text


class TestConfigureNewEvent(TestCase):
    def test_valid_input(self):
        data = {
            "event_name": "my_event",
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                "required": ["name", "age"],
            },
        }
        with app.test_client() as test_client:
            response = test_client.post("/configure_new_event", json=data)
            assert response.status_code == OK
            assert response.text == f"event {data.get('event_name')} added to the DB"

    def test_missing_parameter(self):
        # missing event_name parameter
        data = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        }
        with app.test_client() as test_client:
            response = test_client.post("/configure_new_event", json=data)
            assert response.status_code == BAD_REQUEST
            assert response.text == f"missing required parameter: event_name"

        # missing schema parameter
        with app.test_client() as test_client:
            response = test_client.post(
                "/configure_new_event", json={"event_name": "my_event"}
            )
            assert response.status_code == BAD_REQUEST
            assert response.text == f"missing required parameter: schema"

    def test_invalid_parameter_type(self):
        # event_name is not a string
        data = {
            "event_name": 123,
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
                "required": ["name", "age"],
            },
        }
        with app.test_client() as test_client:
            response = test_client.post("/configure_new_event", json=data)
            assert response.status_code == BAD_REQUEST
            assert response.text == "event_name should be a string"

        # schema is not a json
        data = {"event_name": "my_event", "schema": "hey there"}
        with app.test_client() as test_client:
            response = test_client.post("/configure_new_event", json=data)
            assert response.status_code == BAD_REQUEST
            assert response.text == "schema should be a json"
