from http import HTTPStatus
from typing import Any

from flask import Response, make_response
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError

from src.database import db
from src.models.events import Events


def get_event_names_from_db(event_names: list) -> list:
    return Events.query.filter(Events.event_name.in_(event_names)).all()


def add_entry(entry: db.Model, db_instance: SQLAlchemy) -> None:
    db_instance.session.add(entry)
    db_instance.session.commit()


def validate_request_parameters(request_object: Any, request_body: dict) -> Response:
    try:
        request_object.parse_obj(request_body)
    except ValidationError as e:
        error_message = ""
        for error in e.errors():
            field_name = error["loc"][-1]
            prefix = f"{field_name}: " if field_name != "__root__" else ""
            error_message = ", ".join(
                [f"{prefix}" f"{error['msg']}" for error in e.errors()]
            )
        return make_response(error_message, HTTPStatus.BAD_REQUEST)
