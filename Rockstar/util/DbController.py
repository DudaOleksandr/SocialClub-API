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

    def add_jobs_list(self, job_list, db_user):
        for job in job_list:
            # print(job)
            db_job = self.db_client.get_filter_table('jobs', 'jobId', job.get('jobId'))

            if not db_job:

                db_job = self.db_client.insert_data('jobs', {
                    'jobId': job.get('jobId'),
                    'name': job.get('name'),
                    'desc': job.get('desc'),
                    'url': job.get('url'),
                    'percentage': job.get('percentage'),
                    'type': job.get('type'),
                    'authorId': job.get('authorId'),
                    'imgSrc': job.get('imgSrc')
                })[0]
            else:
                db_job = db_job[0]

                if db_job.get('percentage') != job.get('percentage'):
                    db_job = self.db_client.update_data('jobs', {
                        'percentage': job.get('percentage')
                    }, 'jobId', job.get('jobId'))[0]

            db_user_job = self.db_client.get_filter_table('userJobs', 'jobId', db_job.get('id'))

            is_db_user_job_added = db_user.get('id') in [j.get('userId') for j in db_user_job]

            if not db_user_job and not is_db_user_job_added:
                db_user_job = self.db_client.insert_data('userJobs', {
                    'userId': db_user.get('id'),
                    'jobId': db_job.get('id'),
                    'bookmarked': job.get('bookmarked'),
                    'played': job.get('played')
                })
            else:
                db_user_job = db_user_job[0]

                if db_job.get('bookmarked') != job.get('bookmarked') or db_job.get('played') != job.get('played'):
                    db_user_job = self.db_client.update_data('userJobs', {
                        'bookmarked': job.get('bookmarked'),
                        'played': job.get('played')
                    }, 'jobId', db_job.get('id'))
