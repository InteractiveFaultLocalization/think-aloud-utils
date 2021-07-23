import logging
import os
from typing import Dict, Tuple, Set, Optional, Callable
from typing_extensions import Protocol

import nltk
import pandas

from util.chart import AxisLabel, DistributionChart
from util.keyword import split_keywords, Topic
from util.log import init_local_logger

_logger = init_local_logger(logging.INFO)


def filter_distribution_if_in(distribution: Dict[Tuple[str, str], int], words: Set[str]) -> Dict[Tuple[str, str], int]:
    return {k: v for k, v in distribution.items() if k[0] not in words}


def plot_top_word_distribution(
        distribution: Dict[Tuple[str, str], int], file_name: str, top: int = 10,
        xnote: str = None, ynote: str = None) -> str:
    top_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:top]
    distribution = tuple((str(nltk.tag.tuple2str(key)), int(value)) for key, value in top_items)
    x_label = AxisLabel('lemmatized words', unit='word/original POS', note=xnote)
    y_label = AxisLabel('count of occurrences', unit='paper', note=ynote)
    output_file_name_pdf = f'{file_name}.top{top}.pdf'
    with DistributionChart(distribution, f'{file_name}.top{top}.pdf', x_label=x_label, y_label=y_label):
        ...
    return output_file_name_pdf


class CountLemmasProtocol(Protocol):
    def __call__(
            self,
            papers_details: pandas.DataFrame, relevant_papers: pandas.DataFrame,
            keywords: Optional[Set[str]] = None
    ) -> Dict[Tuple[str, str], int]: ...


def word_distribution_per_topics(
        filename: Callable[[str], str],
        count_lemmas: CountLemmasProtocol,
        papers_details: pandas.DataFrame, relevant_papers: pandas.DataFrame
):
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
    return outputs
