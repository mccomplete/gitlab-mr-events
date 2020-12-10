import copy
import functools
import logging
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import date
from typing import Dict, List, Optional, Mapping, Set, Iterable

from src import settings, gitlab_client
from src.gitlab_client import MergeRequestID

logger = logging.getLogger(__name__)
thread_pool = ThreadPoolExecutor(max_workers=settings.NUMBER_OF_THREADS)


def get_merge_requests_json(project_id: str, since: Optional[date]) -> List[Dict]:
    logger.info(f"Getting events for project {project_id}")
    events = gitlab_client.get_events(project_id, since)
    logger.info(f"Getting merge requests for {len(events)} events")
    merge_request_ids = _get_merge_request_ids(events)
    merge_requests = _get_merge_requests(project_id, merge_request_ids)
    logger.info(
        f"Assembling merge requests JSON from {len(merge_requests)} merge requests"
    )
    return _get_merge_requests_tree(events, merge_requests)


def _get_merge_requests(
    project_id: str, merge_request_ids: Iterable[MergeRequestID]
) -> List[Dict]:
    return [
        merge_request
        for merge_request in thread_pool.map(
            functools.partial(gitlab_client.get_merge_request, project_id),
            merge_request_ids,
        )
        if merge_request is not None
    ]


def _get_merge_requests_tree(
    events: List[Dict], merge_requests: List[Dict]
) -> List[Dict]:
    events_index = _group_by_merge_request(events)
    merge_requests = copy.deepcopy(merge_requests)
    for merge_request in merge_requests:
        merge_request["events"] = events_index[str(merge_request["id"])]

    return merge_requests


def _get_merge_request_ids(events: List[Dict]) -> Set[MergeRequestID]:
    return {
        MergeRequestID(key=str(event["target_id"]), name=event["target_title"])
        for event in events
    }


def _group_by_merge_request(events: List[Dict]) -> Mapping[str, List[Dict]]:
    index = defaultdict(list)
    for event in events:
        key = str(event["target_id"])
        index[key].append(event)

    return index


def _key_by_project_id(projects: List[Dict]) -> Dict[str, Dict]:
    return {str(project["id"]): project for project in projects}
