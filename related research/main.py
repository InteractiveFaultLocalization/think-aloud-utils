from typing import Set
from varname import nameof

import bibtexparser


def print_set(items: Set[str], title: str):
    print(title + "\n" + "=" * len(title))
    items = set(items)
    print('\n'.join(items))
    print()


def main():
    parser = bibtexparser.bparser.BibTexParser(common_strings=True, ignore_nonstandard_types=False)
    with open('1.1phase.bib', 'r', encoding='utf-8') as bibfile:
        bibliography: bibtexparser.bibdatabase.BibDatabase = bibtexparser.load(bibfile, parser)

    journals = {}
    proceedings = {}
    for entry in bibliography.get_entry_list():
        if 'journal' in entry:
            journal = entry['journal']
            journals[journal] = journals.get(journal, 0) + 1
        elif 'booktitle' in entry:
            proceeding = entry['booktitle']
            proceedings[proceeding] = proceedings.get(proceeding, 0) + 1
        else:
            print(f"{entry['title']} ({entry['ENTRYTYPE']}): {';'.join(entry.keys())}")
    print_set(set(journals), nameof(journals))
    print_set(set(proceedings), nameof(proceedings))


if __name__ == '__main__':
    main()
