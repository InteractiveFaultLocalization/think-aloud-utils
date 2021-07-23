from enum import Enum
from typing import Set

KEYWORDS = (
    'think aloud',  # DBLP will yield the dashed version also
    'verbalization',
    'interview',
    'verbal',
    'report',
    'strategy',
    'fault localization',
    'debugging',
    'debug',
    'bug',
    'bugfix'
)


def split_keywords(keywords: Set[str] = KEYWORDS) -> Set[str]:
    words = []
    for keyword in keywords:
        words.extend(keyword.split(' '))
    return set(words)


def drop_keywords(items: Set[str]):
    return items - split_keywords()


class Topic(Enum):
    THINK_ALOUD = {
        'think aloud',
        'verbalization',
        'verbal',
    }

    STRATEGY = {
        'strategy'
    }

    FAULT_LOCALIZATION = {
        'fault localization',
        'debugging',
        'debug'
    }
