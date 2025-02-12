import asyncio

from . import User
from .User import retrieve_rid
from ..util.DbController import DbController
from ..util.Parser import parse_jobs


async def get_jobs_by_username(username, client, token, db_client, number_of_jobs=30):
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
    while not success:
        print(f"Error fetching Rockstar ID: {rid}")
        client.wait_for_bearer_token()
        rid, success = retrieve_rid(username, client.get_token())

    return await fetch_jobs(rid, client, token, number_of_jobs, db_client=db_client)


async def fetch_jobs(rid, client, token, number_of_jobs, db_client, index=0, jobs_list=None):
    """Fetch jobs for a given Rockstar ID with pagination and token renewal."""
    jobs_list = jobs_list or []
    user = User.retrieve_user_from_token(client.get_token())
    db_user = (db_client.get_filter_table('users', 'rockstarId', user.get('nameId')))[0]
    db_controller = DbController(db_client)
    tasks = []
    batch_size = 300

    while True:

        url = f"https://scapi.rockstargames.com/search/mission?dateRangeCreated=any&sort=likes&platform=pc&title=gtav&pageIndex={index}&creatorRockstarId={rid[0]}&pageSize={number_of_jobs}"

        headers = {
            'X-AMC': 'true',
            'Referer': 'https://socialclub.rockstargames.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Authorization': f'Bearer {token}',
        }

        response = client.session.get(url, headers=headers)

        tries = 0
        while response.status_code != 200:
            print(f"Error fetching jobs: {response}")
            if tries >= 1:
                client.wait_for_bearer_token()
            headers['Authorization'] = f'Bearer {client.get_token()}'
            response = client.session.get(url, headers=headers)
            tries += 1

        data = response.json()
        parsed_data = parse_jobs(data)
        print(f"Fetched {len(parsed_data)} jobs from {user.get('nameId')}")
        jobs_list.extend(parsed_data)

        if len(jobs_list) >= batch_size:
            # Call db_controller.add_jobs_list asynchronously without awaiting (runs in background)
            tasks.append(asyncio.create_task(db_controller.add_jobs_list(jobs_list, db_user)))
            print(f"Processed {len(jobs_list)} to DB")
            jobs_list = []

        if not data.get("hasMore", False):
            break

        index += 1
        await asyncio.sleep(3)  # Non-blocking sleep

    await asyncio.gather(*tasks)
    return jobs_list
