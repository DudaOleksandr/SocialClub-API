import time


from .User import retrieve_rid
from ..util.Parser import parseJobs


def get_jobs_by_username(username, client, token, number_of_jobs=30):
    """
    Retrieve jobs created by a specific user.

    Args:
        token: social club bearer token
        username (str): Username for which jobs are to be retrieved.

    Returns:
        dict: JSON response containing job data if successful,
              or error message if an error occurs during the request.
    """

    # Retrieve the user's Rockstar ID
    rid_data, status = retrieve_rid(username, token)
    if status == 0:
        print(f"Error: {rid_data[0]}")
        return {"error": rid_data[0]}

    rid = rid_data[0]

    # Construct headers and URL for the jobs request
    headers = {
        'X-AMC': 'true',
        'Referer': 'https://socialclub.rockstargames.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Authorization': f'Bearer {token}',
        'baggage': 'sentry-environment=prod,sentry-release=2024-07-15dic_prod.sc,sentry-public_key=9c63ab4e6cf94378a829ec7518e1eaf6,sentry-trace_id=cb75881c68684d89b8812b85a07ee572',
        'sentry-trace': 'cb75881c68684d89b8812b85a07ee572-a31057600fd3ef13'
    }

    url = f'https://scapi.rockstargames.com/search/mission?dateRangeCreated=any&sort=likes&platform=pc&title=gtav&creatorRockstarId={rid}&pageSize={number_of_jobs}'

    response = client.session.get(url, headers=headers)
    index = 1
    jobs_list = parseJobs(response.json())
    while response.json()['hasMore']:
        response = get_response_with_access_check(url)
        url = f'https://scapi.rockstargames.com/search/mission?dateRangeCreated=any&sort=likes&platform=pc&title=gtav&pageIndex={index}&creatorRockstarId={rid}&pageSize={number_of_jobs}'

        jobs_list.extend(parseJobs(response.json()))
        index += 1
        if not response.json()['hasMore']:
            response = get_response_with_access_check(url)
            jobs_list.extend(parseJobs(response.json()))
            break

    if response.status_code == 200:
        return jobs_list
    else:
        return {"error": f"Error during the request: {response.status_code}"}


def get_response_with_access_check(url):
    from Main import client
    headers = {
        'X-AMC': 'true',
        'Referer': 'https://socialclub.rockstargames.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Authorization': f'Bearer {client.bearer_token}',
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        'baggage': 'sentry-environment=prod,sentry-release=2024-07-15dic_prod.sc,sentry-public_key=9c63ab4e6cf94378a829ec7518e1eaf6,sentry-trace_id=cb75881c68684d89b8812b85a07ee572',
        'sentry-trace': 'cb75881c68684d89b8812b85a07ee572-a31057600fd3ef13'
    }
    response = client.session.get(url, headers=headers)
    time.sleep(2)
    print(response.status_code)

    if response.status_code != 200:
        client.refresh_token()
        headers_refresh = {
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": client.get_cookies_for_header(),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        try:
            r = client.session.post('https://socialclub.rockstargames.com/connect/refreshaccess',
                                    headers=headers_refresh,
                                    allow_redirects=True,
                                    data="accessToken=" + client.bearer_token)
            filtered_cookies = r.cookies
            if "BearerToken" in filtered_cookies:
                client.session.cookies = filtered_cookies["BearerToken"].value
        except Exception:
            client.refresh_token()

        headers = {
            'X-AMC': 'true',
            "Cache-Control": "no-cache",
    "Pragma": "no-cache",
            'Referer': 'https://socialclub.rockstargames.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Authorization': f'Bearer {client.bearer_token}',
            'baggage': 'sentry-environment=prod,sentry-release=2024-07-15dic_prod.sc,sentry-public_key=9c63ab4e6cf94378a829ec7518e1eaf6,sentry-trace_id=cb75881c68684d89b8812b85a07ee572',
            'sentry-trace': 'cb75881c68684d89b8812b85a07ee572-a31057600fd3ef13'
        }

        response = client.session.get(url, headers=headers)
    return response