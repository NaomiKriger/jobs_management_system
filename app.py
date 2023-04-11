import os
import subprocess
from http.client import OK

from dotenv import load_dotenv
from flask import Flask, make_response, request

from app_helpers import (add_job_entry, add_job_to_job_in_event,
                         get_execution_command,
                         upload_job_to_container_registry)
from app_validations import (UploadJobValidations,
                             configure_new_event_validations)
from aws_operations import ecr_login
from consts import Endpoint
from database import add_entry
from models import Event, db

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@app.route(Endpoint.CONFIGURE_NEW_EVENT.value, methods=["POST"])
def configure_new_event():
    validation_response = configure_new_event_validations()
    if validation_response:
        return validation_response

    event_name = request.json["event_name"]
    add_entry(Event(event_name, request.json["schema"]), db)

    return make_response(f"event {event_name} added to the DB", OK)


@app.route(Endpoint.UPLOAD_JOB.value, methods=["POST"])
def upload_job():
    validation_response = UploadJobValidations.validate_upload_job()
    if validation_response.status_code != OK:
        return validation_response

    job_path = upload_job_to_container_registry(request.json["job_logic"])
    add_job_entry(job_path, db)
    add_job_to_job_in_event(db)

    return make_response(
        f"{upload_job.__name__} finished successfully. {validation_response.get_data().decode('utf-8')}",
        OK,
    )


@app.route("/execute_jobs_by_event", methods=["POST"])
def execute_jobs_by_event():
    return {"message": f"{execute_jobs_by_event.__name__} is executed"}


@app.route("/execute_job_by_image_tag", methods=["POST"])
def execute_job_by_image_tag():
    ecr_login()
    image_tag = request.json.get("image_tag")
    execution_parameters = request.json.get("execution_parameters")
    result = subprocess.run(
        get_execution_command(execution_parameters, image_tag),
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
