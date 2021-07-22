import logging
import os
import re
from typing import Tuple, Optional

import varname

import util.log
import pandas

import requests

from util.dblp import get_dblp_forum_id, get_publication_stream_query
from util.keyword import KEYWORDS

logger = util.log.init_local_logger(logging.INFO)

venue_api_address = 'https://dblp.org/search/venue/api'
publication_api_address = 'https://dblp.uni-trier.de/search/publ/api'

PAGE_SIZE = 1000


def main():
    relevant_papers = pandas.DataFrame()
    papers_details = pandas.DataFrame()
    authors = pandas.DataFrame()

    with open(os.path.join('phase1_1', 'output.manual.txt')) as forums_file:
        for line in forums_file:
            line = line.strip()
            parts = tuple(part for part in line.split('|') if part != '')
            name = parts[0]
            forum_id = get_dblp_forum_id(parts[4])
            publication_stream_query = get_publication_stream_query(forum_id)
            results = requests.get(
                publication_api_address,
                params={'q': publication_stream_query, 'format': 'json', 'h': PAGE_SIZE})
            total_hit_count = int(results.json()['result']['hits']['@total'])
            logger.info(f'there is {total_hit_count} paper published in {name}')
            # DBLP seems to be limited to 10_000 hits to compute, but there is no documentation
            for start_index in range(0, min(total_hit_count, 10_000), PAGE_SIZE):
                logger.info(f'retrieving papers from {start_index} published in {name}')
                results = requests.get(
                    publication_api_address,
                    params={'q': publication_stream_query, 'format': 'json', 'h': PAGE_SIZE, 'f': start_index})
                sent_count = results.json()['result']['hits']['@sent']
                hits = results.json()['result']['hits']['hit']
                print()
                for paper in hits:
                    if 'title' not in paper['info']:
                        print('[!tit]', end='\t')
                        continue
                    title: str = paper['info']['title']
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
                        print('relate', end='\t')
                    else:
                        if doi is not None:
                            if year is not None:
                                print(f'[{year}]', end='\t')
                            else:
                                print('[    ]', end='\t')
                        else:
                            print('[!DOI]', end='\t')

                print()
                logger.info(f'got {sent_count}|{len(hits)} hits')
            relevant_count = relevant_papers['paper id'].drop_duplicates().count()
            logger.info(f'altogether {relevant_count} relevant papers found so far')

        relevant_papers.to_csv(os.path.join('phase1_2', varname.nameof(relevant_papers) + '.csv'))
        papers_details.drop_duplicates().to_csv(os.path.join('phase1_2', varname.nameof(papers_details) + '.csv'))
        authors.drop_duplicates().to_csv(os.path.join('phase1_2', varname.nameof(authors) + '.csv'))


if __name__ == '__main__':
    main()
