import os

from dotenv import load_dotenv
from flask import Flask, Response, make_response

from src.consts import Endpoint
from src.database import db
from src.endpoints.configure_new_event_logic import \
    configure_new_event_response
from src.endpoints.configure_new_job_logic import configure_new_job_response
from src.endpoints.execute_job_by_image_tag_logic import \
    execute_job_by_image_tag_response

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@app.route(Endpoint.CONFIGURE_NEW_EVENT.value, methods=["POST"])
def configure_new_event() -> Response:
    return configure_new_event_response()


@app.route(Endpoint.CONFIGURE_NEW_JOB.value, methods=["POST"])
def configure_new_job() -> Response:
    return configure_new_job_response()


@app.route(Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, methods=["POST"])
def execute_job_by_image_tag() -> Response:
    return execute_job_by_image_tag_response()


@app.route(Endpoint.EXECUTE_JOBS_BY_EVENT.value, methods=["POST"])
def execute_jobs_by_event() -> Response:
    return make_response(f"{execute_jobs_by_event.__name__} is executed")


@app.route(Endpoint.VIEW_EVENT_INFO.value, methods=["GET"])
def view_event_info() -> Response:
    return make_response(f"{view_event_info.__name__} is executed")


@app.route(Endpoint.VIEW_JOB_INFO.value, methods=["GET"])
def view_job_info() -> Response:
    return make_response(f"{view_job_info.__name__} is executed")


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
