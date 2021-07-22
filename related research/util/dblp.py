import re


def get_dblp_forum_id(dblp_web_url: str):
    id_match = re.search(r'/(?P<id>(conf|journals)/[\w0-9]+)/', dblp_web_url)
    if id_match:
        return id_match.group('id')
    else:
        raise ValueError(f'no id found in {dblp_web_url}')


def get_publication_stream_query(forum_id: str) -> str:
    return f'stream:streams/{forum_id}:'
