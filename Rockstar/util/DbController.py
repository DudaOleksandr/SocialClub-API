import asyncio
from functools import wraps, partial


def async_wrapper(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


class DbController:

    def __init__(self, db_client):
        self.db_client = db_client

    def add_user(self, db_user, user):
        if not db_user:
            return self.db_client.insert_data('users', {
                'rockstarId': user.get('nameId'),
                'rockstarName': user.get('nickname')
            })
        else:
            return db_user

    # TODO fix intermittent
    # str has no attribute get and / or
    # Server disconnected without response

    @async_wrapper
    def add_jobs_list(self, job_list, db_user):
        print(f"\nAdding jobs for user {db_user.get('rockstarName')}\n")

        job_ids = [job.get('jobId') for job in job_list]
        existing_jobs = {job['jobId']: job for job in self.db_client.get_filter_table('jobs', 'jobId', job_ids)}

        jobs_to_insert = []
        jobs_to_update = []
        user_jobs_to_insert = []
        user_jobs_to_update = []

        for job in job_list:
            db_job = existing_jobs.get(job.get('jobId'))

            if not db_job:
                jobs_to_insert.append({
                    'jobId': job.get('jobId'),
                    'name': job.get('name'),
                    'desc': job.get('desc'),
                    'url': job.get('url'),
                    'percentage': job.get('percentage'),
                    'type': job.get('type'),
                    'authorId': job.get('authorId'),
                    'imgSrc': job.get('imgSrc')
                })
            elif db_job.get('percentage') != job.get('percentage'):
                jobs_to_update.append({
                    'jobId': job.get('jobId'),
                    'percentage': job.get('percentage')
                })

        if jobs_to_insert:
            print(f"Inserting {len(jobs_to_insert)} jobs")
            inserted_jobs = self.db_client.insert_data('jobs', jobs_to_insert)
            for job in inserted_jobs:
                existing_jobs[job['jobId']] = job

        if jobs_to_update:
            print(f"Updating {len(jobs_to_update)} jobs")
            job_ids_to_update = [job['jobId'] for job in jobs_to_update]
            update_fields = {k: v for job in jobs_to_update for k, v in job.items() if k != 'jobId'}
            self.db_client.update_data('jobs', update_fields, 'jobId', job_ids_to_update)

        job_ids = [job['id'] for job in existing_jobs.values()]
        existing_user_jobs = {
            (uj['userId'], uj['jobId']): uj
            for uj in self.db_client.get_filter_table('userJobs', 'jobId', job_ids)
        }

        for job in job_list:
            db_job = existing_jobs[job.get('jobId')]
            key = (db_user.get('id'), db_job.get('id'))

            if key not in existing_user_jobs:
                user_jobs_to_insert.append({
                    'userId': db_user.get('id'),
                    'jobId': db_job.get('id'),
                    'bookmarked': job.get('bookmarked'),
                    'played': job.get('played')
                })
            else:
                db_user_job = existing_user_jobs[key]
                if db_user_job.get('bookmarked') != job.get('bookmarked') or db_user_job.get('played') != job.get(
                        'played'):
                    user_jobs_to_update.append({
                        'userId': db_user.get('id'),
                        'jobId': db_job.get('id'),
                        'bookmarked': job.get('bookmarked'),
                        'played': job.get('played')
                    })

        if user_jobs_to_insert:
            print(f"Inserting {len(jobs_to_insert)} userJobs")
            self.db_client.insert_data('userJobs', user_jobs_to_insert)

        if user_jobs_to_update:
            print(f"Updating {len(jobs_to_update)} jobs")
            for job in user_jobs_to_update:
                self.db_client.update_data('userJobs', job, ['userId', 'jobId'], [(job['userId'], job['jobId'])])

        print(f"\nFinished with database updates")


