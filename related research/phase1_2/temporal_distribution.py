import logging
import os

import pandas
from matplotlib import pyplot as plt
import matplotlib.ticker as plticker

from util.keyword import to_topic, topic_mapping, topic_markers, Topic

from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)


@log_execution(_logger)
def main(*, papers_details_path: str, relevant_papers_path: str):
    papers_details: pandas.DataFrame = pandas.read_csv(papers_details_path, index_col=0)
    relevant_papers = pandas.read_csv(relevant_papers_path, index_col=0)
    
    relevant_papers['topic'] = relevant_papers['keyword'].map(topic_mapping())
    papers_topic = relevant_papers[['paper id', 'topic']].drop_duplicates()
    papers_topic_with_year = papers_topic.merge(papers_details[['paper id', 'year']], on='paper id')

    count_per_year: pandas.DataFrame = papers_details.groupby('year').count()
    count_per_year_per_topic: pandas.DataFrame = papers_topic_with_year.groupby(['topic', 'year']).count()

    outputs = [display_count(count_per_year, tag='all')]
    for index, topic in enumerate(papers_topic['topic'].drop_duplicates()):
        if isinstance(topic, str):
            topic_counts = count_per_year_per_topic.loc[topic]
            outputs.append(display_count(topic_counts, tag=topic))
    return set(outputs)


def display_count(count_per_year, tag: str):
    human_readable_tag = tag.replace("_", " ").lower()
    figure: plt.Figure
    axes: plt.Axes
    figure, axes = plt.subplots()
    figure.set_size_inches(20, 5)
    axes.bar(
        x=count_per_year.index, height=count_per_year['paper id'], label='all papers',
        color='lightgray', edgecolor='black')
    axes.set_xlabel('publication time [year]')
    axes.set_ylabel(f'count [paper] (related to {human_readable_tag})')
    axes.xaxis.set_major_locator(plticker.MultipleLocator(base=1.0))
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.show()
    paper_per_year_path = os.path.join('phase1_2', 'generated', f'paper_per_year.{tag.lower()}.pdf')
    figure.savefig(paper_per_year_path)
    return paper_per_year_path


if __name__ == '__main__':
    main(
        papers_details_path=os.path.join('phase1_2', 'generated', 'papers_details.csv'),
        relevant_papers_path=os.path.join('phase1_2', 'generated', 'relevant_papers.csv')
    )
