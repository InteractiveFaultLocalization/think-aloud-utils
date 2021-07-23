import logging
import os
from typing import Optional, Set

import nltk
import pandas

from util.chart import AxisLabel, DistributionChart
from util.distribution import filter_distribution_if_in, plot_top_word_distribution
from util.keyword import split_keywords, Topic
from util.natural_language import lemmatize

import tqdm

from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)


@log_execution(_logger)
def main(*, papers_details_mendeley_path: str, relevant_papers_path: str):
    papers_details: pandas.DataFrame = pandas.read_csv(papers_details_mendeley_path, index_col=0)
    relevant_papers: pandas.DataFrame = pandas.read_csv(relevant_papers_path)

    def filename(tag):
        return os.path.join('phase1_2', 'generated', f'distribution_of_mendeley_keywords.{tag}')

    outputs = []

    _logger.info('checking all papers')
    distribution = count_lemmas(papers_details, relevant_papers)
    plot_top_word_distribution(distribution, filename('all'))
    outputs.append(
        plot_top_word_distribution(
            filter_distribution_if_in(distribution, split_keywords()),
            filename('all.no_keywords'),
            xnote='except keywords'))

    for topic in Topic:
        _logger.info(f'checking papers related to {topic}')
        topic_distribution = count_lemmas(
            papers_details, relevant_papers,
            keywords=topic.value
        )
        human_readable_topic_name = topic.name.replace('_', ' ').lower()
        outputs.append(
            plot_top_word_distribution(
                filter_distribution_if_in(topic_distribution, split_keywords(topic.value)),
                filename(topic.name.lower()),
                ynote='related to ' + human_readable_topic_name,
                xnote='except keywords about ' + human_readable_topic_name))

    return tuple(outputs)


def count_lemmas(
        papers_details: pandas.DataFrame,
        relevant_papers: pandas.DataFrame,
        keywords: Optional[Set[str]] = None
):
    distribution = {}
    progress_bar = tqdm.tqdm(
        papers_details.iterrows(),
        desc='counting Mendeley keywords', unit='paper', total=len(papers_details.index))
    for index, paper in progress_bar:
        paper_id = paper['paper id']
        paper_keywords = set(relevant_papers.groupby('paper id').get_group(paper_id)['keyword'])
        raw_keywords = paper['mendeley keywords']
        if keywords is None or keywords & paper_keywords != set():
            if isinstance(raw_keywords, str):
                mendeley_keywords = split_keywords(eval(raw_keywords))
                lemmas = lemmatize(mendeley_keywords)
                for lemma in lemmas:
                    distribution[lemma] = distribution.get(lemma, 0) + 1
    return distribution


if __name__ == '__main__':
    main(
        papers_details_mendeley_path=os.path.join('phase1_2', 'generated', 'papers_details.mendeley.csv'),
        relevant_papers_path=os.path.join('phase1_2', 'generated', 'relevant_papers.csv'))
