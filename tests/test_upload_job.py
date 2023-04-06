import os
import unittest

import pytest

from app import app, db


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


@unittest.skip("Not implemented")
def test_valid_input(test_client):
    """
    expected result: response.status_code == OK, new record added to job table, new record added to job_in_event table
    """
    pass


@unittest.skip("Not implemented")
def test_invalid_job_name(test_client):
    """
    scenarios: job_name is not a string,
    job_name already exists
    """
    pass


@unittest.skip("Not implemented")
def test_invalid_event_names(test_client):
    """
    scenarios: event_names not a list, event names in list are not strings,
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
