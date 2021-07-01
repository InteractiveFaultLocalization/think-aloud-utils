import math
import traceback
from dataclasses import dataclass
from enum import Enum
import pandas

import bibtexparser

from util.bibtex_entry import id_tag_of


class ForumType(Enum):
    JOURNAL = 'journal'
    CONFERENCE = 'conference'


def main():
    forums = pandas.DataFrame()

    parser = bibtexparser.bparser.BibTexParser(common_strings=True, ignore_nonstandard_types=False)
    with open('1.1phase.bib', 'r', encoding='utf-8') as bibfile:
        bibliography: bibtexparser.bibdatabase.BibDatabase = bibtexparser.load(bibfile, parser)

    papers = pandas.DataFrame()
    for entry in bibliography.get_entry_list():
        papers = papers.append(entry, ignore_index=True)

    journals = papers['journal'].drop_duplicates()
    for name in journals:
        if not (isinstance(name, float) and math.isnan(name)):
            published_papers = papers[papers['journal'] == name]
            forums = forums.append({'name': name, 'type': ForumType.JOURNAL, 'papers': published_papers}, ignore_index=True)
    proceedings = papers['booktitle'].drop_duplicates()
    for name in proceedings:
        if not (isinstance(name, float) and math.isnan(name)):
            published_papers = papers[papers['booktitle'] == name]
            forums = forums.append({'name': name, 'type': ForumType.CONFERENCE, 'papers': published_papers}, ignore_index=True)

    def get_refs(refs: pandas.DataFrame):
        try:
            results = refs.apply(id_tag_of, axis=1)
        except Exception as exc:
            traceback.print_exc()
        return results

    refs = forums['papers'].apply(get_refs)
    #forums['paper ref tags'] =

    for entry in forums:
        print(str(forum) + ', '.join(tags))


if __name__ == '__main__':
    main()
