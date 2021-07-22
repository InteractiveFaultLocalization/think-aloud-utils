import logging
import os
from typing import Tuple

import pandas

from util.dblp import get_dblp_forum_id

from util.log import init_local_logger, log_execution

_logger = init_local_logger(level=logging.INFO)


@log_execution(_logger)
def main(*, forums_manually_checked_txt_path: str) -> Tuple[str, ...]:
    forums = pandas.DataFrame()

    with open(forums_manually_checked_txt_path, 'r', encoding='utf8') as wiki_table_file:
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

    forums_manually_checked_csv_path = os.path.join('phase1_1', 'generated', 'forums.manually_checked.csv')
    forums.drop_duplicates().to_csv(forums_manually_checked_csv_path)
    return forums_manually_checked_csv_path,


if __name__ == '__main__':
    main(forums_manually_checked_txt_path=os.path.join('phase1_1', 'forums.manually_checked.txt'))
