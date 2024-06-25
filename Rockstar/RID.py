from requests import Session, get, post
from pickle import load as pickle_load, dump as pickle_dump
from json import load as json_load, dump as json_dump
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from time import time

LOGIN_URL = "https://signin.rockstargames.com/api/login/socialclub"
CSRF_URL = "https://socialclub.rockstargames.com"
MEMBERS_URL = "https://socialclub.rockstargames.com/members"

COOKIES_FILE = "Storage/Cookies.pkl"
TOKEN_FILE = "Storage/Token.json"

# Will only be useful for first login.
# After that, the session will be saved and re-used at startup.
CASTLE_TOKEN = "LicfeloYd1RcH3loVFZcZG1GGXlUY3RUdx9cZl5PfltKYGcvCkWlwVTgbFyjK9a19ypASiamYqatieo5cp73LnbzhRc1x-lqVB_3P9OQhxdroPsEedIPPjyXimW6MqA_AQb1MiyZ90UUlJh3HO-eVh_02A9dpdcSJPyZXhzihBo9wdcLQ7vHAVPCnlRFocwaC6PDE1PUh0of8KBfEd6eTlygxA1dpsEaW96_bj7Z2xof_JxfU9KSWRj63how_YVVHvDYC0Gj2QpdpdkKU8aWXBLnnhVGpsAUQKObMkT3wgNDopQJBJbzsXMB_wxLpcRZFq3Api_UuX0_0NcSNPqYXR_w2xol4JtREvvXC12m2QpTvaRNGvODaRv0k18BtbNfBfyUX1O9pE8R75JIHLzXEkPtxwpDpbQKN9DeE1-1pE0a84NpG_STXwG1k0ga45JIWjHkCkK6xwtcpM4NQ7XHC0mlxwBDpVgycyDW_8KRPDqglCqoV3L30XBiqdkFHebF0f97OXOZ-38G55hKFrqnWwH8hC5784UXNcfbXAGgdqIkkflfI_r-OnAa-j1xB1A_YzpBLj7nQzgV57w66pVHkdmVLvDa9T062DVcmevjX0DJyE1mNdG383OV9zrYNVya2DWSbhbEkFrfOXW4OdwvSCMS-Dlzmvc6e5UI2g"

class RockstarClient:
    """
    A client class to interact with Rockstar Games Social Club API.

    Attributes:
        email (str): Email address used for authentication.
        password (str): Password used for authentication.
        silent (bool): Flag to suppress logging messages.
        bearer_token (str): Bearer token used for API requests.
        token_expiry_time (float): Unix timestamp indicating token expiry time.
        rvt (str): CSRF token retrieved from the Social Club site.
        session (Session): Requests session object for making HTTP requests.
    """

    def __init__(self, email, password, silent):
        """
        Initialize the RockstarClient with provided credentials.

        Args:
            email (str): Email address used for authentication.
            password (str): Password used for authentication.
            silent (bool): Flag to suppress logging messages.
        """
        self.email = email
        self.password = password
        self.silent = silent
        self.bearer_token = None
        self.token_expiry_time = None
        self.rvt = None
        self.session = Session()

    def Log(self, message):
        """
        Log messages if silent mode is not enabled.

        Args:
            message (str): Message to be logged.
        """
        if not self.silent:
            print(message)

    def SaveSession(self, filename):
        """
        Save the current session cookies to a pickle file.

        Args:
            filename (str): Path to the file where session cookies will be saved.
        """
        with open(filename, 'wb') as f:
            pickle_dump(self.session.cookies, f)

    def LoadSession(self, filename):
        """
        Load session cookies from a pickle file into the current session.

        Args:
            filename (str): Path to the file containing session cookies.

        Returns:
            bool: True if session cookies were loaded successfully, False otherwise.
        """
        try:
            with open(filename, 'rb') as f:
                self.session.cookies.update(pickle_load(f))
            return True
        except FileNotFoundError:
            return False

    def ResumeSession(self):
        """
        Attempt to resume a session by making a request to the members URL.

        Returns:
            bool: True if session was resumed successfully (status code 200), False otherwise.
        """
        response = self.session.get(MEMBERS_URL)
        if response.status_code == 200:
            self.Log("Session resumed successfully")
            return True
        else:
            self.Log("Session expired or failed to resume")
            return False

    def SaveTokenData(self):
        """
        Save bearer token and its expiry time to a JSON file.
        """
        with open(TOKEN_FILE, 'w') as f:
            token_data = {
                'bearer_token': self.bearer_token,
                'token_expiry_time': self.token_expiry_time if self.token_expiry_time else None
            }
            json_dump(token_data, f)
            self.Log("Token data saved successfully.")

    def LoadTokenData(self):
        """
        Load bearer token and its expiry time from a JSON file.
        """
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json_load(f)
                self.bearer_token = token_data.get('bearer_token')
                self.token_expiry_time = token_data['token_expiry_time'] if 'token_expiry_time' in token_data else None
                self.Log("Token data loaded successfully.")

        except FileNotFoundError:
            self.Log("Token data file not found.")

    def GetCookiesForHeader(self):
        """
        Get cookies from the session and format them into a header string.

        Returns:
            str: Formatted string of cookies suitable for HTTP headers.
        """
        cookie_dict = self.session.cookies.get_dict()
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])
        return cookie_header

    def FetchCSRFToken(self):
        """
        Fetch CSRF token from the Social Club website.

        Returns:
            str: CSRF token if found, None otherwise.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://socialclub.rockstargames.com/"
        }

        response = self.session.get(CSRF_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            csrf_token_elem = soup.find("input", {"name": "__RequestVerificationToken"})
            if csrf_token_elem:
                return csrf_token_elem.get("value")
        return None

    def RefreshToken(self):
        """
        Refresh the bearer token using a multi-step process.

        Part I: Make a POST request to a specific endpoint to get a refresh code.
        Part II: Use the refresh code to obtain the new bearer token and its expiry time.
        """
        # Part I - Refreshing Code
        url = "https://signin.rockstargames.com/connect/cors/check/rsg"
        headers = {
            "Accept": "*/*",
            "Cookie": self.GetCookiesForHeader(),
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "signin.rockstargames.com",
            "Origin": "https://www.rockstargames.com",
            "Referer": "https://www.rockstargames.com/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            "X-Requested-With": "XMLHttpRequest"
        }

        data = {"fingerprint":"{\"fp\":{\"user_agent\":\"a36e69effb1fe461bbc19c3ebfecce75\",\"language\":\"fr-FR\",\"pixel_ratio\":1,\"timezone_offset\":-120,\"session_storage\":1,\"local_storage\":1,\"indexed_db\":1,\"open_database\":0,\"cpu_class\":\"unknown\",\"navigator_platform\":\"Win32\",\"do_not_track\":\"unknown\",\"regular_plugins\":\"9aba0104cb3ef4a2f279e49dd0781262\",\"canvas\":\"c663e0153ef98a07ed0eab33f19ea289\",\"webgl\":\"434a31bb3916375f4dd767d526e919b7\",\"adblock\":false,\"has_lied_os\":true,\"touch_support\":\"0;false;false\",\"device_name\":\"Chrome on Windows\",\"js_fonts\":\"c38ffa4be84b2a39c33ff510e42e6c4f\"}}","returnUrl":"/rockstar-games-launcher","linkInfo":{"shouldLink":'false',"service":'null',"username":'null',"serviceVisibility":'null'},"events":[{"eventName":"Sign In Form","eventType":"page-view"}]}
        refresh_resp = self.session.post(url, data=data, headers=headers)
        refresh_code = refresh_resp.text[1:-1]
        self.Log(f"Refresh Code : {refresh_code}")

        # Part II - Collecting the Bearer Token
        url = f"https://www.rockstargames.com/auth/gateway.json?code={refresh_code}"
        headers = {
            "Accept": "*/*",
            "Cookie": self.GetCookiesForHeader(),
            "Content-type": "application/json",
            "Referer": "https://www.rockstargames.com/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        final_request = self.session.get(url, headers=headers)
        bearer_token = final_request.json()['bearerToken']
        bearer_expiration = final_request.json()['tokenExpiresTime']

        self.Log(f"Bearer Token : {bearer_token}")
        self.Log(f"Expiration Time : {bearer_expiration}")

        self.bearer_token = bearer_token
        self.token_expiry_time = bearer_expiration
        self.SaveTokenData()

    def IsTokenExpired(self):
        """
        Check if the bearer token is expired.

        Returns:
            bool or float: True if token is expired, float indicating seconds until expiry otherwise.
        """
        if self.token_expiry_time:
            current_time = datetime.utcnow().timestamp() + 3600 * 2
            expiration_time = self.token_expiry_time

            if int(current_time) > int(expiration_time):
                return True
            else:
                time_diff = expiration_time - current_time
                if time_diff < 0:
                    return True
                else:
                    return max(1, time_diff)
        else:
            self.Log("No token expiry time set. Token considered expired.")
            return True

    def RetrieveRID(self, username):
        """
        Retrieve Rockstar ID (RID) and avatar URL for a given username.

        Args:
            username (str): Username for which RID and avatar URL are to be retrieved.

        Returns:
            tuple: Tuple containing (rid, avatar_url) if successful, ("RID not found", "") if RID is not found,
                   or (error_message, "") if an error occurs during the request.
            int: 1 if RID and avatar URL are found, 0 otherwise.
        """

        current_time = datetime.utcnow().timestamp() + 3600 * 2
        expiration_time = self.token_expiry_time

        if self.IsTokenExpired() == True:
            self.Log("Token has expired. Refreshing...")
            self.RefreshToken()
        
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
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

    def Authenticate(self):
        """
        Authenticate the client by logging into the Rockstar Games Social Club API.

        Raises:
            SystemExit: If login fails, exit the program with status code 1.
        """
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": self.GetCookiesForHeader(),
            "Origin": "https://signin.rockstargames.com",
            "Referer": "https://signin.rockstargames.com/signin/user-form?cid=rsg",
            "Content-Type": "application/json",
            'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            "x-castle-request-token": f"{CASTLE_TOKEN}",
            "X-Lang": "en-US",
            "X-Requested-With": "XMLHttpRequest"
        }

        login_data = {
            "email": self.email,
            "password": self.password,
            "keepMeSignedIn": False,
            "fingerprint":"{\"fp\":{\"user_agent\":\"a36e69effb1fe461bbc19c3ebfecce75\",\"language\":\"fr-FR\",\"pixel_ratio\":1,\"timezone_offset\":-120,\"session_storage\":1,\"local_storage\":1,\"indexed_db\":1,\"open_database\":0,\"cpu_class\":\"unknown\",\"navigator_platform\":\"Win32\",\"do_not_track\":\"unknown\",\"regular_plugins\":\"9aba0104cb3ef4a2f279e49dd0781262\",\"canvas\":\"c663e0153ef98a07ed0eab33f19ea289\",\"webgl\":\"434a31bb3916375f4dd767d526e919b7\",\"adblock\":false,\"has_lied_os\":true,\"touch_support\":\"0;false;false\",\"device_name\":\"Chrome on Windows\",\"js_fonts\":\"c38ffa4be84b2a39c33ff510e42e6c4f\"}}",
            "returnUrl": "/rockstar-games-launcher",
            "linkInfo": {"shouldLink": False, "service": None, "username": None, "serviceVisibility": None},
            "events": [{"eventName": "Sign In Form", "eventType": "page-view"}]
        }

        response = self.session.post(LOGIN_URL, headers=headers, json=login_data)

        if response.status_code == 200:
            if "An error occurred while processing your request." in response.text:
                self.Log(f"Please manually provide a Castle Token for first login.")
                exit(1)

            self.Log(f"Logged in !")
            self.SaveSession(COOKIES_FILE)
        elif "Sorry, we are unable to handle your request at this time." in response.text: 
                self.Log(f"Please manually provide a Castle Token for first login.")
                exit(1)
        else:
            self.Log(f"Login failed - {response.status_code}")
            self.Log(response.text)
            exit(1)

    def Startup(self, force_renewing=False):
        """
        Initialize the client session by attempting to load session cookies and token data,
        or authenticate if no session data is found or if forced to renew.

        Args:
            force_renewing (bool, optional): If True, force renewal of session data even if cookies are loaded.

        If session data is loaded successfully and `force_renewing` is False,
        log a success message and load token data.
        If no session data is found or `force_renewing` is True,
        attempt to fetch CSRF token and authenticate the client.
        """
        if self.LoadSession(COOKIES_FILE) and not force_renewing:
            self.Log("Session loaded successfully")
            self.LoadTokenData()
        else:
            self.Log("No session cookies found, authenticating...")
            csrf_token = self.FetchCSRFToken()
            self.rvt = csrf_token
            if not csrf_token:
                self.Log("Error: CSRF Token not found")
                exit()
            else:
                self.Log(f"CSRF Found : {csrf_token}")

            self.Authenticate()