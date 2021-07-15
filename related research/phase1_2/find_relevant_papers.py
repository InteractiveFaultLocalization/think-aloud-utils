import logging
import os
import re
from typing import Tuple
import util.log
import pandas

import requests

logger = util.log.init_local_logger(logging.INFO)

venue_api_address = 'https://dblp.org/search/venue/api'
publication_api_address = 'https://dblp.uni-trier.de/search/publ/api'


def get_publication_stream_query(parts: Tuple[str, ...]) -> str:
    dblp_web_url = parts[4]
    id_match = re.search(r'/(?P<id>(conf|journals)/[\w0-9]+)/', dblp_web_url)
    if id_match:
        dblp_id = id_match.group('id')
        return f'stream:streams/{dblp_id}:'
    else:
        raise ValueError(f'no id found in {parts}')


KEYWORDS = (
    'think aloud',  # DBLP will yield the dashed version also
    'verbalization',
    'interview',
    'verbal',
    'report',
    'strategy',
    'fault localization',
    'debugging',
    'debug',
    'bug',
    'bugfix'
)
PAGE_SIZE = 1000


def main():
    relevant_papers = pandas.DataFrame()

    with open(os.path.join('phase1_1', 'output.manual.txt')) as forums_file:
        for line in forums_file:
            line = line.strip()
            parts = tuple(part for part in line.split('|') if part != '')
            name = parts[0]
            publication_stream_query = get_publication_stream_query(parts)
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
                    paper_id = paper['info']['key']
                    is_relevant = False
                    for keyword in KEYWORDS:
                        if keyword in title.lower():
                            is_relevant = True
                            relevant_papers = relevant_papers.append(
                                {'keyword': keyword, 'paper id': paper_id},
                                ignore_index=True
                            )
                    if is_relevant:
                        print('relate', end='\t')
                    else:
                        if 'year' in paper['info']:
                            year = paper['info']['year']
                            print(f'[{year}]', end='\t')
                        else:
                            print('[    ]', end='\t')
                print()
                logger.info(f'got {sent_count}|{len(hits)} hits')
            relevant_count = relevant_papers['paper id'].drop_duplicates().count()
            logger.info(f'altogether {relevant_count} relevant papers found so far')

        relevant_papers.to_csv(os.path.join('phase1_2', 'relevant_papers.csv'))


if __name__ == '__main__':
    main()
