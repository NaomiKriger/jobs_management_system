import os

import pytest
from dotenv import load_dotenv

from main import app
from src.database import db
from src.models.events import Events
from src.models.jobs import Jobs
from tests.mocks import basic_schema_mock

load_dotenv()

event_name_pre_configured_in_db = "event_name_pre_configured_in_db"
image_tag_1_in_ecr = "sample_job_1_v5"


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
        db.session.add(
            Jobs(
                image_tag_1_in_ecr,
                basic_schema_mock,
                [event_name_pre_configured_in_db],
                365,
            ),
            db,
        )
        db.session.add(
            Jobs("123", basic_schema_mock, [event_name_pre_configured_in_db], 365), db
        )
        db.session.commit()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()
