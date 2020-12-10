import json
import logging
from datetime import datetime

from flask import Flask, make_response, request

from src import merge_requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/projects/<project_id>/merge_requests/", methods=["GET"])
def get_merge_requests(project_id):
    logger.info(f"Handling GET /merge_requests for project {project_id}")
    since = request.args.get("since")
    try:
        since = datetime.strptime(since, "%Y-%m-%d") if since else None
    except ValueError:
        return _make_response_invalid_date(since)

    logger.info(f"Getting merge requests JSON for project {project_id} since {since}")
    response_json = merge_requests.get_merge_requests_json(project_id, since)
    logger.info(f"Returning JSON for {len(response_json)} merge requests")
    return make_response(json.dumps(response_json), 200)


def _make_response_invalid_date(since):
    return make_response(
        {
            "error": (
                f"Invalid date {since}. The date should be in YYYY-MM-DD format, "
                f"for example, 2020-01-01."
            )
        },
        400,
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
