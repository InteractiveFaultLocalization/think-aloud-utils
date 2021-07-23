import argparse
import logging
import os

import find_relevant_papers
import get_paper_keywords_from_mendeley_for_relevant_papers
import relevant_papers_keyword_intersections
import relevant_papers_mendeley_keyword_distribution
import relevant_papers_title_word_distribution

from util.log import init_local_logger, log_execution

_logger = init_local_logger(level=logging.INFO)


@log_execution(_logger)
def run(*,
        forums_manually_checked_csv_path: str, papers_details_path: str, relevant_papers_path: str,
        papers_details_mendeley_path: str,
        analyze_only=False):
    outputs = []
    if not analyze_only:
        outputs.extend(find_relevant_papers.main(forums_manually_checked_csv_path=forums_manually_checked_csv_path))
        outputs.extend(get_paper_keywords_from_mendeley_for_relevant_papers.main(papers_details_path=papers_details_path))
    else:
        _logger.warning('skipping collection tasks, assume their are already done')
    outputs.extend(relevant_papers_keyword_intersections.main(relevant_papers_path=relevant_papers_path))
    relevant_papers_mendeley_keyword_distribution.main(
        papers_details_mendeley_path=papers_details_mendeley_path,
        relevant_papers_path=relevant_papers_path
    )
    relevant_papers_title_word_distribution.main(
        papers_details_path=papers_details_path,
        relevant_papers_path=relevant_papers_path
    )
    return tuple(outputs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--analyze_only', action='store_true', help='skipping the long running collection tasks')
    args = parser.parse_args()

    run(
        forums_manually_checked_csv_path=os.path.join('phase1_1', 'generated', 'forums.manually_checked.csv'),
        papers_details_path=os.path.join('phase1_2', 'generated', 'papers_details.csv'),
        relevant_papers_path=os.path.join('phase1_2', 'generated', 'relevant_papers.csv'),
        papers_details_mendeley_path=os.path.join('phase1_2', 'generated', 'papers_details.mendeley.csv'),

        analyze_only=args.analyze_only
    )
