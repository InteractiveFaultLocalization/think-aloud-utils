import os
from typing import List
import re

import nltk
import pandas

stop_words = set(nltk.corpus.stopwords.words('english'))


def drop_stop_words(tokens: List[str]):
    return [word for word in tokens if not word.lower() in stop_words]


def drop_non_alpha(tokens: List[str]):
    return [word for word in tokens if not re.search(r'[\W0-9]', word)]


def main():
    papers_details = pandas.read_csv(os.path.join('phase1_2', 'papers_details.csv'))
    relevant_papers = pandas.read_csv(os.path.join('phase1_2', 'relevant_papers.csv'))

    distribution = {}

    stemmer = nltk.stem.WordNetLemmatizer()
    for index, paper in papers_details.iterrows():
        title = paper['title']
        tokens = nltk.tokenize.word_tokenize(title.lower())
        cleared_tokens = drop_non_alpha(drop_stop_words(tokens))
        stems = [stemmer.lemmatize(token) for token in cleared_tokens]
        for stem in stems:
            distribution[stem] = distribution.get(stem, 0) + 1

    print('\n'.join([f'{key}: {value}' for key, value in sorted(distribution.items(), key=lambda e: e[1], reverse=True)[:10]]))


if __name__ == '__main__':
    main()
