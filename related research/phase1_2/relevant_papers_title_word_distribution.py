import os
from typing import Optional, Set, List, Tuple

import nltk
import pandas
import tqdm

from util.distribution import filter_distribution_if_in, plot_top_word_distribution
from util.keyword import split_keywords, Topic
from util.natural_language import lemmatize


def main():
    papers_details: pandas.DataFrame = pandas.read_csv(os.path.join('phase1_2', 'papers_details.csv'))
    relevant_papers: pandas.DataFrame = pandas.read_csv(os.path.join('phase1_2', 'relevant_papers.csv'))

    def filename(tag):
        return os.path.join('phase1_2', f'distribution_of_title_words.{tag}')

    distribution = count_lemmas(papers_details, relevant_papers)
    plot_top_word_distribution(distribution, filename('all'))
    plot_top_word_distribution(
        filter_distribution_if_in(distribution, split_keywords()),
        filename('all.no_keywords'),
        xnote='except keywords')

    think_aloud_distribution = count_lemmas(
        papers_details, relevant_papers,
        keywords=Topic.THINK_ALOUD_KEYWORDS.value
    )
    plot_top_word_distribution(
        filter_distribution_if_in(think_aloud_distribution, split_keywords(Topic.THINK_ALOUD_KEYWORDS.value)),
        filename('think_aloud'), ynote='related to think aloud', xnote='except keywords about think aloud')

    fault_localization_distribution = count_lemmas(
        papers_details, relevant_papers,
        keywords=Topic.FAULT_LOCALIZATION_KEYWORDS.value
    )
    plot_top_word_distribution(
        filter_distribution_if_in(fault_localization_distribution, split_keywords(Topic.FAULT_LOCALIZATION_KEYWORDS.value)),
        filename('fault_localization'),
        ynote='related to fault localization', xnote='except keywords about fault localization')

    strategy_distribution = count_lemmas(
        papers_details, relevant_papers,
        keywords=Topic.STRATEGY_KEYWORDS.value
    )
    plot_top_word_distribution(
        filter_distribution_if_in(strategy_distribution, split_keywords(Topic.STRATEGY_KEYWORDS.value)),
        filename('strategy'), ynote='related to strategy', xnote='except keywords about strategy')


def count_lemmas(
        papers_details: pandas.DataFrame,
        relevant_papers: pandas.DataFrame,
        keywords: Optional[Set[str]] = None
):
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
    main()
