import os

from dotenv import load_dotenv

from Rockstar.API import User, Jobs
from Rockstar.DAL.DbClient import DbClient
from Rockstar.RClient import RockstarClient
from Rockstar.util.DbController import DbController

load_dotenv()

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SILENT = bool(int(os.environ['SILENT']))
TARGET = "I_Kasper_I"

client = RockstarClient(EMAIL, PASSWORD, SILENT)
client.startup(force_renewing=False)
db_client = DbClient()

(rid, avatar_url), state = User.retrieve_rid(TARGET, client.get_token())
job_list = Jobs.get_jobs_by_username(TARGET, client.get_token())
user = User.retrieve_user_from_token(client.get_token())
db_user = db_client.get_filter_table('users', 'rockstarId', user.get('nameId'))
if state == 1:
    print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
    print(f"Jobs of player {TARGET} are {job_list}.")
    print(f"Current user is: {user}.")
else:
    print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")


db_controller = DbController(db_client)
db_controller.add_user(db_user, user)
db_controller.add_jobs_list(job_list, db_user)

# response = db.table("jobs").insert(job_list).execute()
# print(response)
