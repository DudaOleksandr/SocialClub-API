from requests import get

def retrieve_rid(username, token):
    """
    Retrieve Rockstar ID (RID) and avatar URL for a given username.

    Args:
        token: social club bearer token
        username (str): Username for which RID and avatar URL are to be retrieved.

    Returns:
        tuple: Tuple containing (rid, avatar_url) if successful, ("RID not found", "") if RID is not found,
               or (error_message, "") if an error occurs during the request.
        int: 1 if RID and avatar URL are found, 0 otherwise.
    """

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'scapi.rockstargames.com',
        'Origin': 'https://socialclub.rockstargames.com',
        'Referer': 'https://socialclub.rockstargames.com/',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    url = f"https://scapi.rockstargames.com/profile/getprofile?nickname={username}&maxFriends=3"
    response = get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data["status"] and "accounts" in data and len(data["accounts"]) > 0:
            rid = data["accounts"][0]["rockstarAccount"]["rockstarId"]
            avatar_url = data["accounts"][0]["rockstarAccount"]["avatarUrl"]
            return (rid, avatar_url), 1
        else:
            return ("RID not found", ""), 0
    else:
        return (f"Error during the request: {response.status_code}", ""), 0

def retrieve_user_from_creds(token):

    headers = {
        "accept": "*/*",
        "accept-language": "uk,uk-UA;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,ru;q=0.5",
        "authorization": f'Bearer {token}',
        "content-type": "application/json",
        "priority": "u=1, i",
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }

    url = "https://graph.rockstargames.com/?origin=https://socialclub.rockstargames.com&operationName=userData&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22074459b15e5c168dd6e9e0b9024ad04fa9804f08ec93e8774707e0695c9e883e%22%7D%7D"

    response = get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return (f"Error during the request: {response.status_code}", ""), 0