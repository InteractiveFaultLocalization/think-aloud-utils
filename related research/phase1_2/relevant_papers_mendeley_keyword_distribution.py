import os

import pandas

from util.keyword import split_keywords
from util.natural_language import lemmatize

import tqdm


def main():
    papers_details = pandas.read_csv(
        os.path.join('phase1_2', 'papers_details.mendeley.csv'), index_col=0)

    lemma_counts = {}
    for index, paper in tqdm.tqdm(papers_details.iterrows(), desc='counting Mendeley keywords', unit='paper', total=len(papers_details.index)):
        raw_keywords = paper['mendeley keywords']
        if isinstance(raw_keywords, str):
            mendeley_keywords = split_keywords(eval(raw_keywords))
            lemmas = lemmatize(mendeley_keywords)
            for lemma in lemmas:
                lemma_counts[lemma] = lemma_counts.get(lemma, 0) + 1
    print()


if __name__ == '__main__':
    main()