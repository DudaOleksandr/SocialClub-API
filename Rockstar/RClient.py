from requests import Session
from pickle import load as pickle_load, dump as pickle_dump
from json import load as json_load, dump as json_dump
from bs4 import BeautifulSoup
from datetime import datetime

LOGIN_URL = "https://signin.rockstargames.com/api/login/socialclub"
CSRF_URL = "https://socialclub.rockstargames.com"
MEMBERS_URL = "https://socialclub.rockstargames.com/members"

COOKIES_FILE = "Cookies.pkl"
TOKEN_FILE = "Token.json"

# Will only be useful for first login.
# After that, the session will be saved and re-used at startup.
CASTLE_TOKEN = "wMnxlLT2mbqy8ZeGuriyioOo95e6jZq6mfGyiLChkLWkjonCezeWP-OdiXx0JKzaKINKD79n-uQ6dCy0vmwxo70SWqnvQLu3usc0x5J_BLuBbXZDuygzyuCuluC6FaK1tzg9t8AAMNjyCEve0wtQmIpJAZeXMFjZ2whGxJ8pZZeOVx-HhEdm3tFRBYyfHweDlkdwx88LVODaBXrey0gEhIhJAoGfT3r_6yp9m58LWNzaR3bS3Axenp8kWcXQClSYjlUHmY9JAZmPR2LW2QZD3pBSAoCRVAfbt1YAhd5WA4aPEDKwNGelv9teCIWJV1KDIzBw-fgrdJeXKWf--y5wm58pZ_77LnCX-AJ32M0EVJftM2mXjFcGh58zWJeXV0mHj1cBhYtfA56fI1jF2gRFhPtWAJfJFG6C4FcRx8w4BOiPSxHzjCMAhpbDJYeOSQGGkVYIgI9LEYeMXQGHhVcBGLdnhJZ61jV8v7Qwai1D1rdUZMbqesyEP0DFWzu8Zz28-hJD2M8CHvzWAkejqBJam8oMHOL-S1TZkjJim9oJHdPaS0PCiuap4LtpVOfQbjG0MGo2tS74NBz9tncYCXZ8xQtlRNz_Z5G3v2cxt79nMbe_ZzG3v2cxt79niMUGFXG3_ycxt79ncff_J3H37Gdit-ksiA4E3GO3ejdhjb9nMbe_ZzC3QMg"


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

    def log(self, message):
        """
        Log messages if silent mode is not enabled.

        Args:
            message (str): Message to be logged.
        """
        if not self.silent:
            print(message)

    def save_session(self, filename):
        """
        Save the current session cookies to a pickle file.

        Args:
            filename (str): Path to the file where session cookies will be saved.
        """
        with open(filename, 'wb') as f:
            pickle_dump(self.session.cookies, f)

    def load_session(self, filename):
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

    def resume_session(self):
        """
        Attempt to resume a session by making a request to the members URL.

        Returns:
            bool: True if session was resumed successfully (status code 200), False otherwise.
        """
        response = self.session.get(MEMBERS_URL)
        if response.status_code == 200:
            self.log("Session resumed successfully")
            return True
        else:
            self.log("Session expired or failed to resume")
            return False

    def save_token_data(self):
        """
        Save bearer token and its expiry time to a JSON file.
        """
        with open(TOKEN_FILE, 'w') as f:
            token_data = {
                'bearer_token': self.bearer_token,
                'token_expiry_time': self.token_expiry_time if self.token_expiry_time else None
            }
            json_dump(token_data, f)
            self.log("Token data saved successfully.")

    def load_token_data(self):
        """
        Load bearer token and its expiry time from a JSON file.
        """
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json_load(f)
                self.bearer_token = token_data.get('bearer_token')
                self.token_expiry_time = token_data['token_expiry_time'] if 'token_expiry_time' in token_data else None
                self.log("Token data loaded successfully.")

        except FileNotFoundError:
            self.log("Token data file not found.")

    def get_token(self):
        if self.is_token_expired():
            self.refresh_token()
            return self.bearer_token
        else:
            return self.bearer_token

    def get_cookies_for_header(self):
        """
        Get cookies from the session and format them into a header string.

        Returns:
            str: Formatted string of cookies suitable for HTTP headers.
        """
        cookie_dict = self.session.cookies.get_dict()
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])
        return cookie_header

    def fetch_csrf_token(self):
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

    def refresh_token(self):
        """
        Refresh the bearer token using a multistep process.

        Part I: Make a POST request to a specific endpoint to get a refresh code.
        Part II: Use the refresh code to obtain the new bearer token and its expiry time.
        """
        # Part I - Refreshing Code
        url = "https://signin.rockstargames.com/connect/cors/check/rsg"
        headers = {
            "Accept": "*/*",
            "Cookie": self.get_cookies_for_header(),
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "signin.rockstargames.com",
            "Origin": "https://www.rockstargames.com",
            "Referer": "https://www.rockstargames.com/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            "X-Requested-With": "XMLHttpRequest"
        }

        data = {
            "fingerprint": "{\"fp\":{\"user_agent\":\"a36e69effb1fe461bbc19c3ebfecce75\",\"language\":\"fr-FR\",\"pixel_ratio\":1,\"timezone_offset\":-120,\"session_storage\":1,\"local_storage\":1,\"indexed_db\":1,\"open_database\":0,\"cpu_class\":\"unknown\",\"navigator_platform\":\"Win32\",\"do_not_track\":\"unknown\",\"regular_plugins\":\"9aba0104cb3ef4a2f279e49dd0781262\",\"canvas\":\"c663e0153ef98a07ed0eab33f19ea289\",\"webgl\":\"434a31bb3916375f4dd767d526e919b7\",\"adblock\":false,\"has_lied_os\":true,\"touch_support\":\"0;false;false\",\"device_name\":\"Chrome on Windows\",\"js_fonts\":\"c38ffa4be84b2a39c33ff510e42e6c4f\"}}",
            "returnUrl": "/rockstar-games-launcher",
            "linkInfo": {"shouldLink": 'false', "service": 'null', "username": 'null', "serviceVisibility": 'null'},
            "events": [{"eventName": "Sign In Form", "eventType": "page-view"}]}
        refresh_resp = self.session.post(url, data=data, headers=headers)
        refresh_code = refresh_resp.text[1:-1]
        self.log(f"Refresh Code : {refresh_code}")

        # Part II - Collecting the Bearer Token
        url = f"https://www.rockstargames.com/auth/gateway.json?code={refresh_code}"
        headers = {
            "Accept": "*/*",
            "Cookie": self.get_cookies_for_header(),
            "Content-type": "application/json",
            "Referer": "https://www.rockstargames.com/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        final_request = self.session.get(url, headers=headers)
        bearer_token = final_request.json()['bearerToken']
        bearer_expiration = final_request.json()['tokenExpiresTime']

        self.log(f"Bearer Token : {bearer_token}")
        self.log(f"Expiration Time : {bearer_expiration}")

        self.bearer_token = bearer_token
        self.token_expiry_time = bearer_expiration
        self.save_token_data()

    def is_token_expired(self):
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
            self.log("No token expiry time set. Token considered expired.")
            return True

    def authenticate(self):
        """
        Authenticate the client by logging into the Rockstar Games Social Club API.

        Raises:
            SystemExit: If login fails, exit the program with status code 1.
        """
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": self.get_cookies_for_header(),
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
            "fingerprint": "{\"fp\":{\"user_agent\":\"a36e69effb1fe461bbc19c3ebfecce75\",\"language\":\"fr-FR\",\"pixel_ratio\":1,\"timezone_offset\":-120,\"session_storage\":1,\"local_storage\":1,\"indexed_db\":1,\"open_database\":0,\"cpu_class\":\"unknown\",\"navigator_platform\":\"Win32\",\"do_not_track\":\"unknown\",\"regular_plugins\":\"9aba0104cb3ef4a2f279e49dd0781262\",\"canvas\":\"c663e0153ef98a07ed0eab33f19ea289\",\"webgl\":\"434a31bb3916375f4dd767d526e919b7\",\"adblock\":false,\"has_lied_os\":true,\"touch_support\":\"0;false;false\",\"device_name\":\"Chrome on Windows\",\"js_fonts\":\"c38ffa4be84b2a39c33ff510e42e6c4f\"}}",
            "returnUrl": "/rockstar-games-launcher",
            "linkInfo": {"shouldLink": False, "service": None, "username": None, "serviceVisibility": None},
            "events": [{"eventName": "Sign In Form", "eventType": "page-view"}]
        }

        response = self.session.post(LOGIN_URL, headers=headers, json=login_data)

        if response.status_code == 200:
            if "An error occurred while processing your request." in response.text:
                self.log(f"Please manually provide a Castle Token for first login.")
                exit(1)

            self.log(f"Logged in !")
            self.save_session(COOKIES_FILE)
        elif "Sorry, we are unable to handle your request at this time." in response.text:
            self.log(f"Please manually provide a Castle Token for first login.")
            exit(1)
        else:
            self.log(f"Login failed - {response.status_code}")
            self.log(response.text)
            exit(1)

    def startup(self, force_renewing=False):
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
        if self.load_session(COOKIES_FILE) and not force_renewing:
            self.log("Session loaded successfully")
            self.load_token_data()
        else:
            self.log("No session cookies found, authenticating...")
            csrf_token = self.fetch_csrf_token()
            self.rvt = csrf_token
            if not csrf_token:
                self.log("Error: CSRF Token not found")
                exit()
            else:
                self.log(f"CSRF Found : {csrf_token}")

            self.authenticate()
