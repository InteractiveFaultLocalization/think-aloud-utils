import logging
import os
import re
from typing import Tuple, Optional

import varname

import util.log
import pandas
import tqdm

import requests

from util.dblp import get_dblp_forum_id, get_publication_stream_query
from util.keyword import KEYWORDS
from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)

venue_api_address = 'https://dblp.org/search/venue/api'
publication_api_address = 'https://dblp.uni-trier.de/search/publ/api'

PAGE_SIZE = 1000


@log_execution(_logger)
def main(*, forums_manually_checked_csv_path: str) -> Tuple[str, ...]:
    forums = pandas.read_csv(forums_manually_checked_csv_path, index_col=0)
    forums['checked paper count'] = 0
    forums['relevant paper count'] = 0

    relevant_papers = pandas.DataFrame()
    papers_details = pandas.DataFrame()
    authors = pandas.DataFrame()

    for index, forum in tqdm.tqdm(forums.iterrows(), desc='scanning forums', unit='forum', total=len(forums.index)):
        forum_id = forum['id']
        forum_abbreviation = forum['abbreviation']
        publication_stream_query = get_publication_stream_query(forum_id)
        results = requests.get(
            publication_api_address,
            params={'q': publication_stream_query, 'format': 'json', 'h': PAGE_SIZE})
        total_hit_count = int(results.json()['result']['hits']['@total'])
        # DBLP seems to be limited to 10_000 hits to compute, but there is no documentation
        with tqdm.tqdm(
                total=min(total_hit_count, 10_000),
                desc=f'inspecting papers of {forum_abbreviation}', unit='paper',
                leave=False
        ) as progress_bar:
            for start_index in range(0, min(total_hit_count, 10_000), PAGE_SIZE):
                results = requests.get(
                    publication_api_address,
                    params={'q': publication_stream_query, 'format': 'json', 'h': PAGE_SIZE, 'f': start_index})
                hits = results.json()['result']['hits']['hit']
                for paper in hits:
                    authors, papers_details, relevant_papers, is_relevant = extract_paper_properties(
                        relevant_papers, papers_details, authors,
                        paper, forum_id)
                    forums.at[index, 'checked paper count'] += 1
                    if is_relevant:
                        forums.at[index, 'relevant paper count'] += 1
                    progress_bar.update(1)

    relevant_papers_path = os.path.join('phase1_2', 'generated', varname.nameof(relevant_papers) + '.csv')
    papers_details_path = os.path.join('phase1_2', 'generated', varname.nameof(papers_details) + '.csv')
    authors_path = os.path.join('phase1_2', 'generated', varname.nameof(authors) + '.csv')
    forums_path = os.path.join('phase1_2', 'generated', 'forums_with_statistics.csv')
    relevant_papers.to_csv(relevant_papers_path)
    papers_details.drop_duplicates().to_csv(papers_details_path)
    authors.drop_duplicates().to_csv(authors_path)
    forums.drop_duplicates().to_csv(forums_path)

    return relevant_papers_path, papers_details_path, authors_path, forums_path


def extract_paper_properties(relevant_papers, papers_details, authors, paper, forum_id):
    title: Optional[str] = None
    if 'title' in paper['info']:
        title = paper['info']['title']
    else:
        _logger.error(f'{paper} does not have a tilte in the DBLP')
        return authors, papers_details, relevant_papers, False
    year: Optional[int] = None
    if 'year' in paper['info']:
        year = paper['info']['year']
    paper_id = paper['info']['key']
    if 'venue' in paper['info']:
        forum = paper['info']['venue']
    else:
        forum = paper['info']['publisher']
    doi = None
    if 'doi' in paper['info']:
        doi = paper['info']['doi']
    is_relevant = False
    for keyword in KEYWORDS:
        if keyword in title.lower():
            is_relevant = True
            relevant_papers = relevant_papers.append(
                {'keyword': keyword, 'paper id': paper_id},
                ignore_index=True
            )
    if is_relevant:
        papers_details = papers_details.append(
            {
                'paper id': paper_id,
                'doi': doi,
                'title': title,
                'year': year,
                'forum': forum,
                'forum id': forum_id
            },
            ignore_index=True
        )
        if 'authors' in paper['info'] and 'author' in paper['info']['authors']:
            if isinstance(paper['info']['authors']['author'], list):
                for author in paper['info']['authors']['author']:
                    authors = authors.append(
                        {
                            'paper id': paper_id,
                            'author id': author['@pid'],
                            'name': author['text']
                        },
                        ignore_index=True
                    )
            else:
                author = paper['info']['authors']['author']
                authors = authors.append(
                    {
                        'paper id': paper_id,
                        'author id': author['@pid'],
                        'name': author['text']
                    },
                    ignore_index=True
                )
        else:
            authors = authors.append(
                {
                    'paper id': paper_id,
                    'author id': None,
                    'name': None
                },
                ignore_index=True
            )
    return authors, papers_details, relevant_papers, is_relevant


if __name__ == '__main__':
    main(forums_manually_checked_csv_path=os.path.join('phase1_1', 'generated', 'forums.manually_checked.csv'))
