import os
from typing import Dict, Tuple, Set

import nltk

from util.chart import AxisLabel, DistributionChart


def filter_distribution_if_in(distribution: Dict[Tuple[str, str], int], words: Set[str]) -> Dict[Tuple[str, str], int]:
    return {k: v for k, v in distribution.items() if k[0] not in words}


def plot_top_word_distribution(
        distribution: Dict[Tuple[str, str], int], file_name: str, top: int = 10,
        xnote: str = None, ynote: str = None):
    top_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:top]
    distribution = tuple((str(nltk.tag.tuple2str(key)), int(value)) for key, value in top_items)
    x_label = AxisLabel('lemmatized words', unit='word/original POS', note=xnote)
    y_label = AxisLabel('count of occurrences', unit='paper', note=ynote)
    with DistributionChart(distribution, f'{file_name}.top{top}.pdf', x_label=x_label, y_label=y_label):
        ...
