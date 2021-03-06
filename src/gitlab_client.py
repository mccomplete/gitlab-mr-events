import logging
from datetime import date
from typing import Dict, List, Optional, NamedTuple

import requests
import tenacity
from tenacity import stop_after_attempt, wait_exponential

from src import settings


logger = logging.getLogger(__name__)


class MergeRequestID(NamedTuple):
    key: str
    name: str


def get_merge_request(project_id: str, mrid: MergeRequestID) -> Optional[Dict]:
    response = _gitlab_api_request(
        f"projects/{project_id}/merge_requests",
        {"scope": "all", "search": mrid.name, "in": "title"},
    )
    merge_requests = [
        merge_request
        for merge_request in response.json()
        if str(merge_request["id"]) == mrid.key
    ]
    if len(merge_requests) == 1:
        return merge_requests[0]

    return None


def get_events(project_id: str, since: Optional[date]) -> List[Dict]:
    page = 0
    total_pages = None
    events = []
    while (total_pages is None) or (page < total_pages):
        page += 1
        logger.info(
            f"Requesting page {page} of events from gitlab for project {project_id}"
        )
        params = {"target_type": "merge_request", "page": page, "per_page": 100}
        if since:
            params["after"] = str(since)

        response = _gitlab_api_request(f"projects/{project_id}/events", params)
        events += response.json()
        total_pages = int(response.headers["x-total-pages"])

    return events


def _gitlab_api_request(endpoint, params):
    response = _http_get(
        f"https://gitlab.com/api/{settings.GITLAB_API_VERSION}/{endpoint}",
        params=params,
        headers={"PRIVATE-TOKEN": settings.GITLAB_PRIVATE_TOKEN},
    )
    _log_rate_limit(endpoint, params, response)
    return response


@tenacity.retry(
    stop=stop_after_attempt(settings.NUMBER_OF_RETRIES),
    wait=wait_exponential(),
)
def _http_get(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    logger.info(
        f"GET request for {url} with params {params} "
        f"returned in {response.elapsed.total_seconds()} seconds",
    )
    response.raise_for_status()
    return response


def _log_rate_limit(endpoint, params, response):
    headers = response.headers
    logger.info(
        f"GET request for {endpoint} with params {params} "
        f"returned with rate limit {headers['ratelimit-limit']} "
        f"requests per second, {headers['ratelimit-observed']} "
        f"requests so far, {headers['ratelimit-remaining']} remaining"
    )
