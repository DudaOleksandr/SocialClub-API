import time

from . import User
from .User import retrieve_rid
from ..util.DbController import DbController
from ..util.Parser import parseJobs


def get_jobs_by_username(username, client, token, db_client, number_of_jobs=30):
    """
    Retrieve jobs created by a specific user.

    Args:
        db_client: Database client for interacting with the database.
        username (str): Username for which jobs are to be retrieved.
        client: API client handling requests and token management.
        token (str): Social Club bearer token.
        number_of_jobs (int, optional): Number of jobs to retrieve. Defaults to 30.

    Returns:
        list: List of parsed job data if successful.
        dict: Error message if an error occurs.
    """

    rid, success = retrieve_rid(username, token)
    if not success:
        print(f"Error fetching Rockstar ID: {rid}")
        return retry_with_new_token(username, client, number_of_jobs, db_client=db_client, is_rid=False)

    return fetch_jobs(rid, client, token, number_of_jobs, db_client=db_client)


def fetch_jobs(rid, client, token, number_of_jobs, db_client, index=0, jobs_list=None):
    """Fetch jobs for a given Rockstar ID with pagination and token renewal."""
    jobs_list = jobs_list or []
    user = User.retrieve_user_from_token(client.get_token())
    db_user = db_client.get_filter_table('users', 'rockstarId', user.get('nameId'))[0]
    db_controller = DbController(db_client)

    while True:
        if index == 0:
            url = f"https://scapi.rockstargames.com/search/mission?dateRangeCreated=any&sort=likes&platform=pc&title=gtav&creatorRockstarId={rid[0]}&pageSize={number_of_jobs}"
        else:
            url = f"https://scapi.rockstargames.com/search/mission?dateRangeCreated=any&sort=likes&platform=pc&title=gtav&pageIndex={index}&creatorRockstarId={rid[0]}&pageSize={number_of_jobs}"
        headers = {
            'X-AMC': 'true',
            'Referer': 'https://socialclub.rockstargames.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Authorization': f'Bearer {token}',
            'baggage': 'sentry-environment=prod,sentry-release=2024-07-15dic_prod.sc,sentry-public_key=9c63ab4e6cf94378a829ec7518e1eaf6,sentry-trace_id=cb75881c68684d89b8812b85a07ee572',
            'sentry-trace': 'cb75881c68684d89b8812b85a07ee572-a31057600fd3ef13'
        }

        response = client.session.get(url, headers=headers)
        if response.status_code != 200:
            # Retry with current index and collected jobs_list
            return retry_with_new_token(rid, client, number_of_jobs, is_rid=True, db_client=db_client, index=index,
                                        jobs_list=jobs_list)

        data = response.json()
        parsed_data = parseJobs(data)
        jobs_list.extend(parsed_data)

        if not data.get("hasMore", False):
            break

        index += 1
        db_controller.add_jobs_list(parsed_data, db_user)
        print(f'\nAdded {len(parsed_data)} jobs to the database for user {user.get("nickname")}.\n')

    return jobs_list


def retry_with_new_token(identifier, client, number_of_jobs, is_rid, db_client, index=0, jobs_list=None):
    """Request a new token and retry fetching jobs, resuming from the last index."""
    client.wait_for_bearer_token()
    new_token = client.get_token()

    if is_rid:
        # Resume fetching with existing RID, current index, and jobs_list
        return fetch_jobs(identifier, client, new_token, number_of_jobs, db_client, index, jobs_list or [])
    else:
        # Retry from the beginning with username to fetch RID again
        return get_jobs_by_username(identifier, client, new_token, db_client, number_of_jobs)

