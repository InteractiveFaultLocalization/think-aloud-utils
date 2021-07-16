import os
from typing import Optional, Set, List, Tuple

import nltk
import pandas

from util.keyword import split_keywords, drop_keywords, Topic
from util.natural_language import drop_non_alpha, drop_stop_words, get_wordnet_pos

import matplotlib.pyplot as plt

from util.string import part_before


def main():
    papers_details: pandas.DataFrame = pandas.read_csv(os.path.join('phase1_2', 'papers_details.csv'))
    relevant_papers: pandas.DataFrame = pandas.read_csv(os.path.join('phase1_2', 'relevant_papers.csv'))

    def drop_distribution_in(distribution, words: Set[str]):
        return {k: v for k, v in distribution.items() if k[0] not in words}

    distribution = count_lemmas(papers_details, relevant_papers)
    plot_distribution(distribution, 'all')
    plot_distribution(
        drop_distribution_in(distribution, split_keywords()),
        'dropped_keywords',
        xnote='(except keywords)')

    think_aloud_distribution = count_lemmas(
        papers_details, relevant_papers,
        keywords=Topic.THINK_ALOUD_KEYWORDS.value
    )
    plot_distribution(
        drop_distribution_in(think_aloud_distribution, split_keywords(Topic.THINK_ALOUD_KEYWORDS.value)),
        'think_aloud', ynote='(related to think aloud)', xnote='(except keywords about think aloud)')

    fault_localization_distribution = count_lemmas(
        papers_details, relevant_papers,
        keywords=Topic.FAULT_LOCALIZATION_KEYWORDS.value
    )
    plot_distribution(
        drop_distribution_in(fault_localization_distribution, split_keywords(Topic.FAULT_LOCALIZATION_KEYWORDS.value)),
        'fault_localization',
        ynote='(related to fault localization)', xnote='(except keywords about fault localization)')

    strategy_distribution = count_lemmas(
        papers_details, relevant_papers,
        keywords=Topic.STRATEGY_KEYWORDS.value
    )
    plot_distribution(
        drop_distribution_in(strategy_distribution, split_keywords(Topic.STRATEGY_KEYWORDS.value)),
        'strategy', ynote='(related to strategy)', xnote='(except keywords about strategy)')


def count_lemmas(
        papers_details: pandas.DataFrame,
        relevant_papers: pandas.DataFrame,
        keywords: Optional[Set[str]] = None
):
    distribution = {}
    for index, paper in papers_details.iterrows():
        paper_id = paper['paper id']
        paper_keywords = set(relevant_papers.groupby('paper id').get_group(paper_id)['keyword'])
        if keywords is None or keywords & paper_keywords != set():
            title = paper['title']
            lemmas = extract_lemmas(title)
            for lemma in lemmas:
                distribution[lemma] = distribution.get(lemma, 0) + 1
    return distribution


def extract_lemmas(title: str) -> List[Tuple[str, str]]:
    stemmer = nltk.stem.WordNetLemmatizer()
    tokens = nltk.tokenize.word_tokenize(title.lower())
    cleared_tokens = drop_non_alpha(drop_stop_words(tokens))
    pos_tokens = [pos_tagged for pos_tagged in nltk.pos_tag(tokens) if pos_tagged[0] in cleared_tokens]
    wordnet_pos_tokens = [(token, get_wordnet_pos(pos), pos) for token, pos in pos_tokens if
                          get_wordnet_pos(pos) is not None]
    lemmas = [(stemmer.lemmatize(token, pos=wordnet_pos), treebank_pos) for token, wordnet_pos, treebank_pos in
              wordnet_pos_tokens]
    return lemmas


def plot_distribution(distribution, tag: str, top: int = 10, xnote: str = None, ynote: str = None):
    fig: plt.Figure
    ax: plt.Axes
    fig, ax = plt.subplots()
    bars = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:top]
    ax.bar(
        x=[nltk.tag.tuple2str(e[0]) for e in bars], height=[e[1] for e in bars],
        color='lightgray', edgecolor='black'
    )
    fig.set_size_inches(12, 6)
    ax.set_xlabel(f'lemmatized words of titles [word/POS]{part_before(xnote)}')
    ax.set_ylabel(f'count of occurrences [paper]{part_before(ynote)}')
    fig.autofmt_xdate()
    fig.show()
    fig.savefig(os.path.join('phase1_2', f'distribution_of_top_{top}_title_words.{tag}.pdf'))


if __name__ == '__main__':
    main()
