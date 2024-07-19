from dataclasses import dataclass


class Job:
    jobId: str
    name: str
    desc: str
    url: str
    imgSrc: str
    authorId: int
    percentage: int
    type: str
    bookmarked: bool
    played: bool
