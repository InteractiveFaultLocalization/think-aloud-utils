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


topic_markers = {
    Topic.THINK_ALOUD: 'o',
    Topic.STRATEGY: 'd',
    Topic.FAULT_LOCALIZATION: 'v'
}


def to_topic(keyword: str):
    for topic in Topic:
        for _keyword in topic.value:
            if _keyword == keyword:
                return topic


def topic_mapping():
    mapping = {}
    for topic in Topic:
        for keyword in topic.value:
            mapping[keyword] = topic.name
    return mapping
