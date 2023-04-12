import os
import subprocess
from http.client import OK

from dotenv import load_dotenv
from flask import Flask, make_response, request

from app_helpers import (add_record_to_job_table, add_record_to_job_in_event_table,
                         get_execution_command)
from app_validations import (ConfigureJobValidations,
                             validate_configure_new_event)
from aws_operations import ecr_login
from consts import Endpoint
from database import add_entry, db
from models.event import Event

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@app.route(Endpoint.CONFIGURE_NEW_EVENT.value, methods=["POST"])
def configure_new_event():
    validation_response = validate_configure_new_event()
    if validation_response:
        return validation_response

    event_name = request.json["event_name"]
    add_entry(Event(event_name, request.json["schema"]), db)

    return make_response(f"event {event_name} added to the DB", OK)


@app.route(Endpoint.CONFIGURE_NEW_JOB.value, methods=["POST"])
def configure_new_job():
    validation_response = ConfigureJobValidations.validate_job_parameters()
    if validation_response.status_code != OK:
        return validation_response

    add_record_to_job_table(db)
    add_record_to_job_in_event_table(db)

    return make_response(
        f"{configure_new_job.__name__} finished successfully. {validation_response.get_data().decode('utf-8')}",
        OK,
    )


@app.route("/execute_jobs_by_event", methods=["POST"])
def execute_jobs_by_event():
    return {"message": f"{execute_jobs_by_event.__name__} is executed"}


@app.route("/execute_job_by_image_tag", methods=["POST"])
def execute_job_by_image_tag():
    ecr_login()
    result = subprocess.run(
        get_execution_command(),
        capture_output=True,
        text=True,
    )

    return {"output": result.stdout, "error": result.stderr}


@app.route("/view_event_metadata", methods=["GET"])
def view_event_metadata():
    return {"message": f"{view_event_metadata.__name__} is executed"}


@app.route("/view_job_metadata", methods=["GET"])
def view_job_metadata():
    return {"message": f"{view_job_metadata.__name__} is executed"}


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
