from dataclasses import dataclass


@dataclass(init=False)
class Job:
    name: str
    desc: str
    url: str
    authorId: int
    percentage: int
    type: str
    bookmarked: bool
    played: bool
