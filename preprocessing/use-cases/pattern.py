from enum import Enum


class Sentiment(Enum):
    POSITIVE = 1
    NATURAL = 2
    NEGATIVE = 4


class Tool(Enum):
    ECLEMMA = 8
    ATLAS = 16
    IFL = 32


class Pattern(object):
    def __init__(self, sentiment: Sentiment, tool: Tool, precondition, change):
        self.change = change
        self.precondition = precondition
        self.tool = tool
        self.sentiment = sentiment

    @property
    def code(self):
        return self.sentiment.value + self.tool.value

    def short_md(self, collection):
        return f'**({collection.id_of(self)})** {self.change}'

    def short_txt(self, collection):
        return f'({collection.id_of(self)}) {self.change}'
