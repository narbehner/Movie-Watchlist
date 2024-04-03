from dataclasses import dataclass, field
from datetime import datetime

#dataclass is a code generator, will make simple code more robust (?)

#attribute : type <-- python type hinting
@dataclass
class Movie:
    _id: str
    title: str
    director: str
    year: int
    cast: list[str] = field(default_factory=list)   #u can replace 'list' with any other callable that generates the default value you want to use for the field.
    series: list[str] = field(default_factory=list)
    last_watched: datetime = None
    rating: int = 0
    tags: list[str] = field(default_factory=list)
    description: str = None
    video_link: str = None