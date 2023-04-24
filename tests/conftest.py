import os

import pytest
from dotenv import load_dotenv

from main import app
from src.database import db
from src.models.events import Events
from tests.mocks import basic_schema_mock

load_dotenv()

event_name_pre_configured_in_db = "event_name_pre_configured_in_db"


@pytest.fixture(scope="session")
def test_client():
    app.config["TESTING"] = True
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI_TEST")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        db.session.add(Events(event_name_pre_configured_in_db, basic_schema_mock), db)
        db.session.commit()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()
