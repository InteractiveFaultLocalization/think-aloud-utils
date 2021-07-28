import logging
import os

import pandas
import matplotlib.pyplot as plt

from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)


@log_execution(_logger)
def main(*, forums_with_statistics_path: str):
    forums = pandas.read_csv(forums_with_statistics_path, index_col=0)

    figure: plt.Figure
    axes: plt.Axes
    figure, axes = plt.subplots()
    figure.set_size_inches(30, 5)
    sorted_entry = forums.sort_values('checked paper count', ascending=False)
    relevant_counts = sorted_entry['relevant paper count']
    total_counts = sorted_entry['checked paper count']
    irrelevant_counts = total_counts - relevant_counts
    percents = relevant_counts / total_counts
    axes.bar(
        x=sorted_entry['id'], height=irrelevant_counts,
        color='gray', edgecolor='black')
    bars = axes.bar(
        x=sorted_entry['id'], height=relevant_counts, bottom=irrelevant_counts,
        color='lightgray', edgecolor='black')
    axes.set_ylim(0, max(total_counts) * 1.15)

    labels = [f'{percent:.2%}' for percent in percents]
    for rect, label in zip(bars, labels):
        height = rect.get_height()
        axes.text(
            rect.get_x() + rect.get_width() / 2, rect.get_y() + height,
            label,
            ha="center", va="bottom", rotation=45
        )

    axes.set_xlabel('DBLP id of forums [type/abbreviation]')
    axes.set_ylabel('count [paper] [percent of relevant papers]\n(accessible papers\' limit on DBLP is 10000)')
    axes.set_title(f'altogether {sum(relevant_counts)} papers found relevant of {sum(total_counts)} checked papers'
                   f' of {len(total_counts)} forums')

    figure.autofmt_xdate()
    figure.show()

    count_statistics_for_forums_path = os.path.join('phase1_2', 'generated', 'count_statistics_for_forums.pdf')
    figure.savefig(count_statistics_for_forums_path)
    return count_statistics_for_forums_path,


if __name__ == '__main__':
    main(forums_with_statistics_path=os.path.join('phase1_2', 'generated', 'forums_with_statistics.csv'))
