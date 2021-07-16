from typing import List, Union, Set

import pandas
import os
import networkx
import varname

from util.keyword import Topic
from util.settool import powerset


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


def main():
    relevant_papers = pandas.read_csv(
        os.path.join('phase1_2', 'relevant_papers.csv'),
        index_col=0
    )
    keywords = relevant_papers['keyword'].drop_duplicates()
    paper_ids = relevant_papers['paper id'].drop_duplicates()

    by_keywords = relevant_papers.groupby('keyword')

    intersections = {}
    for selection in powerset(keywords):
        selected_groups = [by_keywords.get_group(keyword)['paper id'] for keyword in selection]
        intersection = multi_intersection(selected_groups)
        intersections[selection] = intersection

    top_tier_intersections_of_keywords(list(intersections.items()), keywords, tag='all', top=20)
    top_tier_intersections_of_keywords(
        filter_intersections_by_keywords(intersections, Topic.THINK_ALOUD_KEYWORDS.value), keywords,
        varname.nameof(Topic.THINK_ALOUD_KEYWORDS), top=20)
    top_tier_intersections_of_keywords(
        filter_intersections_by_keywords(intersections, Topic.STRATEGY_KEYWORDS.value), keywords,
        varname.nameof(Topic.STRATEGY_KEYWORDS), top=20)
    top_tier_intersections_of_keywords(
        filter_intersections_by_keywords(intersections, Topic.FAULT_LOCALIZATION_KEYWORDS.value), keywords,
        varname.nameof(Topic.FAULT_LOCALIZATION_KEYWORDS), top=20)


def top_tier_intersections_of_keywords(intersections: List, keywords, tag: str, top: int = 10):
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
    networkx.write_graphml(
        top_tier_intersection_keywords_graph,
        os.path.join('phase1_2', f'top_{top}_intersection_keywords.{tag}.graphml'))


if __name__ == '__main__':
    main()
