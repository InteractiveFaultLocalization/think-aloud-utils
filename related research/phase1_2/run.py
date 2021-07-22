import logging
import os

import find_relevant_papers

from util.log import init_local_logger, log_execution

_logger = init_local_logger(level=logging.INFO)


@log_execution(_logger)
def run(*, forums_manually_checked_csv_path: str):
    outputs = []
    outputs.extend(find_relevant_papers.main(forums_manually_checked_csv_path=forums_manually_checked_csv_path))
    return tuple(outputs)


if __name__ == '__main__':
    run(
        forums_manually_checked_csv_path=os.path.join('phase1_1', 'generated', 'forums.manually_checked.csv')
    )
