import logging
from typing import List, Union, Set

import pandas
import os
import networkx
import tqdm
import varname

from util.keyword import Topic
from util.settool import powerset

from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)


def multi_intersection(groups: List[pandas.Series]):
    if groups:
        intersection = groups[0]
        for group in groups[1:]:
            intersection = intersection[intersection.isin(group)]
        return intersection
    else:
        return pandas.Series(dtype=str)


def filter_intersections_by_keywords(intersections, keywords: Set[str]):
    filtered_intersections = list(filter(
        lambda e: set(e[0]) & keywords,
        intersections.items()))
    return filtered_intersections


@log_execution(_logger)
def main(*, relevant_papers_path: str):
    relevant_papers = pandas.read_csv(relevant_papers_path, index_col=0)

    keywords = relevant_papers['keyword'].drop_duplicates()
    powerset_of_keywords = tuple(powerset(keywords))
    by_keywords = relevant_papers.groupby('keyword')

    intersections = {}
    for selection in tqdm.tqdm(powerset_of_keywords, desc='computing keyword intersections', unit='permutation'):
        selected_groups = [by_keywords.get_group(keyword)['paper id'] for keyword in selection]
        intersection = multi_intersection(selected_groups)
        intersections[selection] = intersection

    outputs = [
        top_tier_intersections_of_keywords(list(intersections.items()), keywords, tag='all', top=20),
        top_tier_intersections_of_keywords(
            filter_intersections_by_keywords(intersections, Topic.THINK_ALOUD.value), keywords,
            varname.nameof(Topic.THINK_ALOUD).lower(), top=20),
        top_tier_intersections_of_keywords(
            filter_intersections_by_keywords(intersections, Topic.STRATEGY.value), keywords,
            varname.nameof(Topic.STRATEGY).lower(), top=20),
        top_tier_intersections_of_keywords(
            filter_intersections_by_keywords(intersections, Topic.FAULT_LOCALIZATION.value), keywords,
            varname.nameof(Topic.FAULT_LOCALIZATION).lower(), top=20),
    ]
    return tuple(outputs)


def top_tier_intersections_of_keywords(intersections: List, keywords, tag: str, top: int = 10) -> str:
    top_tier_intersection_keywords_graph = networkx.Graph()
    for keyword in keywords:
        top_tier_intersection_keywords_graph.add_node(keyword, type='keyword', title=keyword)
    for selection, intersection in sorted(intersections, key=lambda e: len(e[1]), reverse=True)[:top]:
        count = len(intersection)
        if count > 0:
            count_id = f'count of {", ".join(selection)}'
            top_tier_intersection_keywords_graph.add_node(count_id, type='count', title=str(count), count=count)
            for keyword in selection:
                top_tier_intersection_keywords_graph.add_edge(keyword, count_id)
    intersection_keywords_graph_path = os.path.join('phase1_2', 'generated', f'intersection_keywords.{tag}.top{top}.graphml')
    networkx.write_graphml(top_tier_intersection_keywords_graph, intersection_keywords_graph_path)
    return intersection_keywords_graph_path


if __name__ == '__main__':
    main(relevant_papers_path=os.path.join('phase1_2', 'generated', 'relevant_papers.csv'))
