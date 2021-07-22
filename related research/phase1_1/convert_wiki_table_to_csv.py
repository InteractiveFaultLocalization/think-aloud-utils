import os
import pandas

from util.dblp import get_dblp_forum_id


def main():
    forums = pandas.DataFrame()

    with open(os.path.join('phase1_1', 'forums.manually_checked.txt'), 'r', encoding='utf8') as wiki_table_file:
        for line in wiki_table_file:
            line = line.strip()
            parts = tuple(part for part in line.split('|') if part != '')
            entry = {
                'name': parts[0],
                'abbreviation': parts[1],
                'type': get_dblp_forum_id(parts[4]).split('/')[0],
                'homepage': parts[3],
                'dblp': parts[4],
                'forum': get_dblp_forum_id(parts[4])
            }
            forums = forums.append(entry, ignore_index=True)
            
    forums.drop_duplicates().to_csv(os.path.join('phase1_1', 'forums.manually_checked.csv'))


if __name__ == '__main__':
    main()
