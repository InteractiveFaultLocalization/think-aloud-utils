import random
from pattern import Pattern, Sentiment, Tool


class PatternCollection(list):
    def __init__(self, *items: Pattern):
        super().__init__()
        self.extend(items)

    def id_of(self, item: Pattern) -> float:
        return float(f'{item.code}.{self.index(item)}') / 2

    def choose(self, count: int):
        _self = self[:]
        random.shuffle(_self)
        collected_patterns = []
        pattern: Pattern
        for pattern in _self:
            if pattern.code not in [p.code for p in collected_patterns]:
                collected_patterns.append(pattern)
            if len(collected_patterns) == count:
                break
        else:
            raise ValueError(f'not enough patterns defined to select {count} try {len(set([p.code for p in self]))}')
        return collected_patterns

    @staticmethod
    def load_from(path: str):
        collection = PatternCollection()
        with open(path, 'r', encoding='utf8') as csv:
            next(csv)
            for line in csv:
                line = line.strip()
                parts = line.split(';')
                tool = None
                sentiment = None
                for t in Tool:
                    if parts[0] == t.name:
                        tool = t
                        break
                for s in Sentiment:
                    if parts[1] == s.name:
                        sentiment = s
                        break
                change = parts[2]
                collection.append(Pattern(sentiment, tool, '', change))
        return collection


patterns = PatternCollection.load_from('case.csv')
