import os
from http.client import OK

from flask import Flask, make_response, request

from app_validations import configure_new_event_validations
from database import add_entry
from models import Event, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@app.route("/configure_new_event", methods=["POST"])
def configure_new_event():
    validation_response = configure_new_event_validations(Event)
    if validation_response:
        return validation_response

    event_name = request.json["event_name"]
    add_entry(Event(event_name, request.json["schema"]), db)

    return make_response(f"event {event_name} added to the DB", OK)


@app.route("/upload_job", methods=["POST"])
def upload_job():
    return {"message": f"{upload_job.__name__} is executed"}


@app.route("/execute_jobs_by_event", methods=["POST"])
def execute_jobs_by_event():
    return {"message": f"{execute_jobs_by_event.__name__} is executed"}


@app.route("/execute_job_by_id", methods=["POST"])
def execute_job_by_id():
    return {"message": f"{execute_job_by_id.__name__} is executed"}


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
