import logging
import os
from typing import Optional, Set, List, Tuple, Callable, Dict

import nltk
import pandas
import tqdm

from util.distribution import filter_distribution_if_in, plot_top_word_distribution, word_distribution_per_topics
from util.keyword import split_keywords, Topic
from util.natural_language import lemmatize

from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)


@log_execution(_logger)
def main(*, papers_details_path: str, relevant_papers_path: str) -> Tuple[str, ...]:
    papers_details: pandas.DataFrame = pandas.read_csv(papers_details_path)
    relevant_papers: pandas.DataFrame = pandas.read_csv(relevant_papers_path)

    def filename(tag):
        return os.path.join('phase1_2', 'generated', f'distribution_of_title_words.{tag}')

    # callback protocols currently are not supported by PyCharm :(
    outputs = word_distribution_per_topics(filename, count_lemmas, papers_details, relevant_papers)
    return tuple(outputs)


def count_lemmas(
        papers_details: pandas.DataFrame,
        relevant_papers: pandas.DataFrame,
        keywords: Optional[Set[str]] = None
) -> Dict[Tuple[str, str], int]:
    distribution = {}
    progress_bar = tqdm.tqdm(
        papers_details.iterrows(),
        desc='counting words of titles', unit='paper', total=len(papers_details.index))
    for index, paper in progress_bar:
        paper_id = paper['paper id']
        paper_keywords = set(relevant_papers.groupby('paper id').get_group(paper_id)['keyword'])
        if keywords is None or keywords & paper_keywords != set():
            title = paper['title']
            lemmas = extract_lemmas(title)
            for lemma in lemmas:
                distribution[lemma] = distribution.get(lemma, 0) + 1
    return distribution


def extract_lemmas(title: str) -> List[Tuple[str, str]]:
    tokens = nltk.tokenize.word_tokenize(title.lower())
    return lemmatize(tokens)


if __name__ == '__main__':
    main(
        papers_details_path=os.path.join('phase1_2', 'generated', 'papers_details.csv'),
        relevant_papers_path=os.path.join('phase1_2', 'generated', 'relevant_papers.csv')
    )
