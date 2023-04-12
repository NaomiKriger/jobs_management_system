import os

from dotenv import load_dotenv
from flask import Flask

from consts import Endpoint
from database import db
from endpoints_logic.configure_new_event import configure_new_event_response
from endpoints_logic.configure_new_job import configure_new_job_response
from endpoints_logic.execute_job_by_image_tag import \
    execute_job_by_image_tag_response

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@app.route(Endpoint.CONFIGURE_NEW_EVENT.value, methods=["POST"])
def configure_new_event():
    return configure_new_event_response()


@app.route(Endpoint.CONFIGURE_NEW_JOB.value, methods=["POST"])
def configure_new_job():
    return configure_new_job_response()


@app.route("/execute_jobs_by_event", methods=["POST"])
def execute_jobs_by_event():
    return {"message": f"{execute_jobs_by_event.__name__} is executed"}


@app.route("/execute_job_by_image_tag", methods=["POST"])
def execute_job_by_image_tag():
    return execute_job_by_image_tag_response()


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
