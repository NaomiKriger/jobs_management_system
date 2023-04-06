import os
from http.client import BAD_REQUEST, OK

import pytest

from app import app, db
from consts import Endpoint


@pytest.fixture(scope="module")
def test_client():
    app.config["TESTING"] = True
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI_TEST")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()


# TEST INDEX

def test_index(test_client):
    response = test_client.get("/")
    assert response.status_code == OK
    json_response = response.get_json()
    assert json_response == {"message": "Welcome to the jobs management system!"}
    assert "Welcome to the jobs management system!" in response.text


# TEST CONFIGURE NEW EVENT #

def test_valid_input(test_client):
    data = {
        "event_name": "my_event",
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        },
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
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json={"event_name": "my_event"})
    assert response.status_code == BAD_REQUEST
    assert response.text == "missing required parameter: schema"


def test_invalid_parameter_type(test_client):
    # event_name is not a string
    data = {
        "event_name": 123,
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        },
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
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        },
    }
    test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    response = test_client.post(Endpoint.CONFIGURE_NEW_EVENT.value, json=data)
    assert response.status_code == BAD_REQUEST
    assert response.text == f"event {data.get('event_name')} already exists"
