import os

import pytest
from dotenv import load_dotenv

from app import app
from database import db
from models.event import Event
from tests.mocks import basic_schema_mock

load_dotenv()


@pytest.fixture(scope="session")
def test_client():
    app.config["TESTING"] = True
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI_TEST")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        db.session.add(Event("test_event_1", basic_schema_mock), db)
        db.session.commit()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()
