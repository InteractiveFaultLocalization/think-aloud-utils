import logging
import os

import collect_raw_list_of_forums
import convert_wiki_table_to_csv

from util.log import init_local_logger, log_execution

_logger = init_local_logger(level=logging.INFO)


@log_execution(_logger)
def run(*, raw_papers_path: str, forums_manually_checked_txt_path: str):
    outputs = []
    outputs.extend(collect_raw_list_of_forums.main(raw_papers_path=raw_papers_path))
    _logger.warning(f'The file {forums_manually_checked_txt_path} should be prepared manually.'
                    ' Assuming you already done it.')
    outputs.extend(convert_wiki_table_to_csv.main(forums_manually_checked_txt_path=forums_manually_checked_txt_path))
    return tuple(outputs)


if __name__ == '__main__':
    run(
        raw_papers_path=os.path.join('phase1_1', 'raw_papers.bib'),
        forums_manually_checked_txt_path=os.path.join('phase1_1', 'forums.manually_checked.txt')
    )
