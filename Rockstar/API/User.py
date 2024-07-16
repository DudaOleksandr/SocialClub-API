import jwt
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


def retrieve_user_from_token(token):
    payload = jwt.decode(token, options={"verify_signature": False})

    result = {
        'nameId': payload.get('nameid'),
        'nickname': payload.get('scAuth.Nickname')
    }
    return result
