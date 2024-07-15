import os
from dotenv import load_dotenv
from Rockstar.RID import RockstarClient

load_dotenv()

# Constants
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SILENT = os.environ['SILENT']

TARGET = "TARGET"

# Main script to retrieve RID and avatar URL
client = RockstarClient(EMAIL, PASSWORD, SILENT)
client.Startup(force_renewing=True)
(rid, avatar_url), state = client.RetrieveRID(TARGET)

# Results
if state == 1:
    print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
else:
    print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")