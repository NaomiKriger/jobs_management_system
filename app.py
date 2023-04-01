from http.client import BAD_REQUEST, OK

from flask import Flask, make_response, request

app = Flask(__name__)

# TEMP MOCK TABLE
events = {}


@app.route("/")
def index():
    return {"message": "Welcome to the jobs management system!"}


@app.route("/configure_new_event", methods=["POST"])
def configure_new_event():
    try:
        event_name = request.json["event_name"]
        schema = request.json["schema"]
    except KeyError as e:
        return make_response(f"missing required parameter: {e.args[0]}", BAD_REQUEST)

    if not isinstance(event_name, str):
        return make_response("event_name should be a string", BAD_REQUEST)
    if not isinstance(schema, dict):
        return make_response("schema should be a json", BAD_REQUEST)

    if event_name in events:
        return make_response(f"event {event_name} already exists", BAD_REQUEST)

    events.update({event_name: schema})
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
    app.run(host="0.0.0.0", port=5000, debug=True)
