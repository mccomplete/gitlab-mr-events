import json
import logging
from datetime import datetime

from flask import Flask, make_response, request

from src import merge_requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/refresh", methods=["GET"])
def refresh():
    logger.info("Handling GET /refresh")
    since = request.args.get("since")
    try:
        since = datetime.strptime(since, "%Y-%m-%d") if since else None
    except ValueError:
        return make_response({"error": f"Invalid date {since}"}, 400)

    logger.info(
        f"Getting merge requests JSON since {since if since else 'the beginning of time'}"
    )
    response_json = merge_requests.get_merge_requests_json(since)
    logger.info(f"Returning JSON for {len(response_json)} merge requests")
    return make_response(json.dumps(response_json), 200)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
