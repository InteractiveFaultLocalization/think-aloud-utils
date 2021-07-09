import os
import re
from typing import Tuple

import requests

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


def main():
    with open(os.path.join('phase1_1', 'output.manual.txt')) as forums_file:
        for line in forums_file:
            line = line.strip()
            parts = tuple(part for part in line.split('|') if part != '')
            name = parts[0]
            publication_stream_query = get_publication_stream_query(parts)
            results = requests.get(
                publication_api_address,
                params={'q': publication_stream_query, 'format': 'json'})
            print(results.json()['result']['hits']['@total'])


if __name__ == '__main__':
    main()
