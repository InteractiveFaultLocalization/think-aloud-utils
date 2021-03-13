from enum import Enum


class Sentiment(Enum):
    POSITIVE = 1
    NATURAL = 2
    NEGATIVE = 4


class Usefulness(Enum):
    HARMFUL = 8
    IRRELEVANT = 16
    HELPFUL = 32


class Pattern(object):
    def __init__(self, title, sentiment: Sentiment, usefulness: Usefulness, precondition, change):
        self.change = change
        self.precondition = precondition
        self.usefulness = usefulness
        self.sentiment = sentiment
        self.title = title

    @property
    def code(self):
        return self.sentiment.value + self.usefulness.value

    def full_md(self, collection):
        return (
            f"## ({collection.id_of(self)}) {self.title}\n"
            f"**szentiment:** {self.sentiment.name}  \n"
            f"**megoldást:** {self.usefulness.name}\n"
            f"### Előfeltétel\n"
            f"{self.precondition}\n"
            f"### Módosítás\n"
            f"{self.change}\n"
        )

    def short_md(self, collection):
        return f'**({collection.id_of(self)})** {self.change}'

    def short_txt(self, collection):
        return f'({collection.id_of(self)}) {self.change}'
