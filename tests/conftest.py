import os

import pytest

from app import app, db


@pytest.fixture(scope="session")
def test_client():
    app.config["TESTING"] = True
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI_TEST"
    )
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()
