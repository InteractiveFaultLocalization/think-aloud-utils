from dataclasses import dataclass
from enum import Enum
from typing import Set
from varname import nameof

import bibtexparser


class ForumType(Enum):
    JOURNAL = 'journal'
    CONFERENCE = 'conference'


@dataclass
class Forum:
    name: str
    kind: ForumType

    def __str__(self):
        return f'|{self.name}|{self.kind.value}|'

    def __hash__(self) -> int:
        return self.name.__hash__()


def main():
    parser = bibtexparser.bparser.BibTexParser(common_strings=True, ignore_nonstandard_types=False)
    with open('1.1phase.bib', 'r', encoding='utf-8') as bibfile:
        bibliography: bibtexparser.bibdatabase.BibDatabase = bibtexparser.load(bibfile, parser)

    forums = {}
    for entry in bibliography.get_entry_list():
        if 'journal' in entry:
            name = entry['journal']
            kind = ForumType.JOURNAL
        elif 'booktitle' in entry:
            name = entry['booktitle']
            kind = ForumType.CONFERENCE
        else:
            print(f"{entry['title']} ({entry['ENTRYTYPE']}): {';'.join(entry.keys())}")
            continue
        forum = Forum(name, kind)
        forums[forum] = forums.get(forum, []) + [entry]

    for forum in forums:
        print(forum)


if __name__ == '__main__':
    main()
