from dataclasses import dataclass


class Job:
    jobId: str
    name: str
    desc: str
    url: str
    authorId: int
    percentage: int
    type: str
    bookmarked: bool
    played: bool
