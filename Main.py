import os
from dotenv import load_dotenv
from Rockstar.API import User, Jobs
from Rockstar.RClient import RockstarClient

load_dotenv()

# Constants
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SILENT = bool(int(os.environ['SILENT']))

TARGET = "O_D_I_U_M"

# # Main script to retrieve RID and avatar URL
# client = RockstarClient(EMAIL, PASSWORD, SILENT)
# client.Startup(force_renewing=True)
# (rid, avatar_url), state = client.RetrieveRID(TARGET)
#
# # Results
# if state == 1:
#     print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
# else:
#     print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")

client = RockstarClient(EMAIL, PASSWORD, SILENT)
client.startup(force_renewing=False)
(rid, avatar_url), state = User.retrieve_rid(TARGET, client.get_token())
jobs = Jobs.get_jobs_by_username(TARGET, client.get_token())

if state == 1:
    print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
    print(f"Jobs of player {TARGET} are {jobs}.")
else:
    print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")
