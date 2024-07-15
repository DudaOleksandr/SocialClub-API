from Rockstar.model.Job import Job


class Parser:

    def parseJobs(self, jsonResponse):
        jobs_list = []

        for item in jsonResponse['content']['items']:
            job_details = Job()

            job_details.name = item['name']
            job_details.desc = item['desc']
            job_details.url = "https://socialclub.rockstargames.com/job/gtav/" + item['id']
            job_details.percentage = int(item['likeCount'] / (item['likeCount'] + item['dislikeCount']))
            job_details.type = item['type']
            job_details.bookmarked = item['bookmarked']
            job_details.played = item['played']

            jobs_list.append(job_details)
        return jobs_list
