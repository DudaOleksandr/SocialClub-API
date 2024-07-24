import json

from Rockstar.model.Job import Job


def parseJobs(jsonResponse):
    jobs_list = []
    for item in jsonResponse['content']['items']:
        job_details = Job()
        job_details.name = item['name']
        job_details.desc = item['desc']
        job_details.jobId = item['id']
        job_details.url = "https://socialclub.rockstargames.com/job/gtav/" + item['id']
        job_details.authorId = item['userId']
        if (item['likeCount'] + item['dislikeCount']) > 0:
            job_details.percentage = round(item['likeCount'] / (item['likeCount'] + item['dislikeCount']) * 100)
        else:
            job_details.percentage = 0
        job_details.type = item['type']
        job_details.bookmarked = item['bookmarked']
        job_details.played = item['played']
        job_details.imgSrc = item['imgSrc']

        jobs_list.append(json.loads(json.dumps(job_details.__dict__)))
        print(job_details.__dict__)
    return jobs_list
