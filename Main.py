import os

from dotenv import load_dotenv

from Rockstar.API import User, Jobs
from Rockstar.DAL.DbClient import DbClient
from Rockstar.RClient import RockstarClient
from Rockstar.model.Creators import getCreatorsDict
from Rockstar.util.DbController import DbController

load_dotenv()

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SILENT = bool(int(os.environ['SILENT']))

client = RockstarClient(EMAIL, PASSWORD, SILENT)
client.startup(force_renewing=False)
db_client = DbClient()
count = 0
# creator = "I_Kasper_I"
user = User.retrieve_user_from_token(client.get_token())
db_user = db_client.get_filter_table('users', 'rockstarId', user.get('nameId'))[0]
for creator in getCreatorsDict():
    # time.sleep(10)
    # if count >= 20:

    # print(creator)
    # time.sleep(5)
    # (rid, avatar_url), state = User.retrieve_rid(creator, client.get_token())
    # time.sleep(5)

    job_list = Jobs.get_jobs_by_username(creator,client, client.get_token())
    # if state == 1:
    #     print(f"RID of player {creator} is {rid}.\nAvatar URL : {avatar_url}")
    #     print(f"Jobs of player {creator} are {job_list}.")
    #     print(f"Current user is: {user}.")
    # else:
    #     print(f"An error occured while retriving the Rockstar ID of player {creator}.")

    db_controller = DbController(db_client)
    # db_controller.add_user(db_user, user)
    db_controller.add_jobs_list(job_list, db_user)

# response = db.table("jobs").insert(job_list).execute()
# print(response)
