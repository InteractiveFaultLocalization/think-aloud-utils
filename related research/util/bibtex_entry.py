from typing import Dict


def id_tag_of(entry: Dict):
    if 'doi' in entry:
        return f"ref:doi:{entry['doi']}"
    elif 'isbn' in entry:
        return f"ref:isbn:{entry['isbn']}"
    elif 'issn' in entry:
        return f"ref:issn:{entry['issn']}"
    elif 'arxivid' in entry:
        return f"ref:arxiv:{entry['arxivid']}"
    else:
        ...
        #raise ValueError(f'Missing ID for {entry["title"]}')
