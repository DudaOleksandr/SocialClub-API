import os
from dotenv import load_dotenv
from supabase import create_client

from Rockstar.API import User, Jobs
from Rockstar.RClient import RockstarClient
from Rockstar.util.Parser import parseJobs

load_dotenv()
# Constants

url = os.environ['DB_URL']
key = os.environ['DB_KEY']
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SILENT = bool(int(os.environ['SILENT']))
TARGET = "TARGET"

db = create_client(url, key)
client = RockstarClient(EMAIL, PASSWORD, SILENT)
client.startup(force_renewing=False)
(rid, avatar_url), state = User.retrieve_rid(TARGET, client.get_token())
jobs = Jobs.get_jobs_by_username(TARGET, client.get_token())
user = User.retrieve_user_from_token(client.get_token())
job_list = parseJobs(jobs)
if state == 1:
    print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
    print(f"Jobs of player {TARGET} are {job_list}.")
    print(f"Current user is: {user}.")
else:
    print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")

response = db.table("jobs").insert(job_list).execute()
print(response)
