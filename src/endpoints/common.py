from flask_sqlalchemy import SQLAlchemy

from src.database import db
from src.models.events import Events


def get_event_names_from_db(event_names: list) -> list:
    return Events.query.filter(Events.event_name.in_(event_names)).all()


def add_entry(entry: db.Model, db_instance: SQLAlchemy) -> None:
    db_instance.session.add(entry)
    db_instance.session.commit()
