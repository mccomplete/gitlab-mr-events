import itertools
import logging
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import date
from typing import Optional, Dict, List

from src import settings, gitlab_client, schema
from src.gitlab_client import MergeRequestID


SUPPORTED_ACTIONS = ["opened", "closed", "reopened"]
logger = logging.getLogger(__name__)
thread_pool = ThreadPoolExecutor(max_workers=settings.NUMBER_OF_THREADS)


def get_merge_requests_json(since: Optional[date]) -> List[Dict]:
    logger.info("Getting projects from gitlab")
    projects = gitlab_client.get_projects()
    logger.info("Getting events for %s projects", len(projects))
    project_ids = _get_project_ids(projects)
    events = _get_events(project_ids, since)
    logger.info("Getting merge requests for %s events", len(events))
    merge_request_ids = _get_merge_request_ids(events)
    merge_requests = _get_merge_requests(merge_request_ids)
    logger.info(
        "Assembling merge requests JSON from %s merge requests", len(merge_requests)
    )
    return _get_merge_requests_tree(events, merge_requests, projects)


def _get_merge_requests(merge_request_ids: List[MergeRequestID]) -> List[Dict]:
    return [
        merge_request
        for merge_request in thread_pool.map(
            gitlab_client.get_merge_request, merge_request_ids
        )
        if merge_request is not None
    ]


def _get_events(project_ids: List[str], since: Optional[date]) -> List[Dict]:
    events: List = [
        event
        for event in itertools.chain.from_iterable(
            thread_pool.map(
                lambda project_id: gitlab_client.get_events(project_id, since),
                project_ids,
            )
        )
        if event["action_name"] in SUPPORTED_ACTIONS
    ]
    return events


def _get_project_ids(projects: List[Dict]) -> List[str]:
    return [str(project["id"]) for project in projects]


def _get_merge_requests_tree(events, merge_requests, projects):
    merge_requests_json = []
    projects_index = _key_by_project_id(projects)
    events_index = _group_by_merge_request(events)
    for merge_request in merge_requests:
        merge_requests_json.append(
            schema.get_merge_request_with_events_list(
                merge_request,
                events=events_index[str(merge_request["id"])],
                project=projects_index[str(merge_request["project_id"])],
            )
        )

    return merge_requests_json


def _get_merge_request_ids(events: List[Dict]) -> List[MergeRequestID]:
    return list(
        {
            MergeRequestID(key=str(event["target_id"]), name=event["target_title"])
            for event in events
        }
    )


def _group_by_merge_request(events: List[Dict]) -> Dict[str, List[Dict]]:
    index = defaultdict(list)
    for event in events:
        index[str(event["target_id"])].append(event)

    return dict(index)


def _key_by_project_id(projects: List[Dict]) -> Dict[str, Dict]:
    return {str(project["id"]): project for project in projects}
