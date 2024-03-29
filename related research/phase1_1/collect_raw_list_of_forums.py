import logging
import math
import os
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

import pandas

import bibtexparser

from util.bibtex_entry import id_tag_of

from util.log import init_local_logger, log_execution

_logger = init_local_logger(level=logging.INFO)


class ForumType(Enum):
    JOURNAL = 'journal'
    CONFERENCE = 'conference'


@log_execution(_logger)
def main(*, raw_papers_path: str) -> Tuple[str, ...]:
    parser = bibtexparser.bparser.BibTexParser(common_strings=True, ignore_nonstandard_types=False)
    with open(raw_papers_path, 'r', encoding='utf-8') as bibfile:
        bibliography: bibtexparser.bibdatabase.BibDatabase = bibtexparser.load(bibfile, parser)

    papers = pandas.DataFrame()
    for entry in bibliography.get_entry_list():
        papers = papers.append(entry, ignore_index=True)

    forums = collect_publications(papers, 'journal', ForumType.JOURNAL)
    forums = forums.append(collect_publications(papers, 'booktitle', ForumType.CONFERENCE), ignore_index=True)

    def collect_refs(related_papers: pandas.DataFrame):
        try:
            refs = related_papers.apply(id_tag_of, axis=1).values.tolist()
            return refs
        except ValueError:
            return None

    forums['refs'] = forums['papers'].apply(collect_refs)

    raw_list_of_forums_path = os.path.join('phase1_1', 'generated', 'raw_list_of_forums.csv')
    forums.to_csv(raw_list_of_forums_path, columns=['name', 'type', 'refs'])
    return raw_list_of_forums_path,


def collect_publications(papers: pandas.DataFrame, column_name: str, forum_type: ForumType):
    forums = pandas.DataFrame()
    for name in papers[column_name].drop_duplicates():
        if not (isinstance(name, float) and math.isnan(name)):
            published_papers = papers[papers[column_name] == name]
            forums = forums.append({
                'name': name,
                'type': forum_type,
                'papers': published_papers},
                ignore_index=True)
    return forums


if __name__ == '__main__':
    main(raw_papers_path=os.path.join('phase1_1', 'raw_papers.bib'))
