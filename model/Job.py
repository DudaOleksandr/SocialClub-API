from dataclasses import dataclass


@dataclass(init=False)
class Job:
    name: str
    desc: str
    url: str
    percentage: int
    type: str
    bookmarked: bool
    played: bool
