import os
from dotenv import load_dotenv

from Rockstar.API import User, Jobs
from Rockstar.RClient import RockstarClient
from Rockstar.util.Parser import parseJobs
from Rockstar.DAL.DbClient import DbClient

load_dotenv()
# Constants

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SILENT = bool(int(os.environ['SILENT']))
TARGET = "TARGET"

rockstar_client = RockstarClient(EMAIL, PASSWORD, SILENT)
rockstar_client.startup(force_renewing=False)
(rid, avatar_url), state = User.retrieve_rid(TARGET, rockstar_client.get_token())
jobs = Jobs.get_jobs_by_username(TARGET, rockstar_client.get_token())
user = User.retrieve_user_from_token(rockstar_client.get_token())
job_list = parseJobs(jobs)
if state == 1:
    print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
    print(f"Jobs of player {TARGET} are {job_list}.")
    print(f"Current user is: {user}.")
else:
    print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")

#TODO Separate logic

db_client = DbClient()

db_user = db_client.get_filter_table('users', 'rockstarId', user.get('nameId'))

if not db_user:
    db_user = db_client.insert_data('users',
                                    {
                                        'rockstarId': user.get('nameId'),
                                        'rockstarName': user.get('nickname')
                                    })
else:
    db_user = db_user[0]

for job in job_list:

    db_job = db_client.get_filter_table('jobs', 'jobId', job.get('jobId'))

    if not db_job:
        db_job = db_client.insert_data('jobs', {
            'jobId': job.get('jobId'),
            'name': job.get('name'),
            'desc': job.get('desc'),
            'url': job.get('url'),
            'percentage': job.get('percentage'),
            'type': job.get('type'),
            'authorId': job.get('authorId')
        })[0]
    else:
        db_job = db_job[0]

        if db_job.get('percentage') != job.get('percentage'):
            db_job = db_client.update_data('jobs', {
                'percentage': job.get('percentage')
            }, 'jobId', job.get('jobId'))

    db_user_job = db_client.get_filter_table('userJobs', 'jobId', db_job.get('id'))

    if not db_user_job:
        db_user_job = db_client.insert_data('userJobs', {
            'userId': db_user.get('id'),
            'jobId': db_job.get('id'),
            'bookmarked': job.get('bookmarked'),
            'played': job.get('played')
        })
    else:
        db_user_job = db_user_job[0]

        if db_job.get('bookmarked') != job.get('bookmarked') or db_job.get('played') != job.get('played'):
            db_user_job = db_client.update_data('userJobs', {
                'bookmarked': job.get('bookmarked'),
                'played': job.get('played')
            }, 'jobId', db_job.get('id'))

# response = db.table("jobs").insert(job_list).execute()
# print(response)
