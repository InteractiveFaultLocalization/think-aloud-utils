import logging
import os
from typing import Tuple

import mendeley
import mendeley.models.catalog
import mendeley.exception
import pandas
import tqdm

import varname

from util.log import init_local_logger, log_execution

_logger = init_local_logger(logging.INFO)


@log_execution(_logger)
def main(*, papers_details_path: str) -> Tuple[str, ...]:
    papers_details = pandas.read_csv(papers_details_path, index_col=0)
    papers_details['mendeley keywords'] = None
    papers_details['publication ids'] = None
    papers_details['mendeley keywords'] = papers_details['mendeley keywords'].astype('object')
    papers_details['publication ids'] = papers_details['publication ids'].astype('object')

    mendeley_client = mendeley.Mendeley(
        "10572",
        client_secret="egcetJherqDH0tJ5")

    auth = mendeley_client.start_client_credentials_flow()
    session = auth.authenticate()

    progress_bar = tqdm.tqdm(
        papers_details.iterrows(),
        desc='getting details from Mendeley', unit='paper', total=len(papers_details.index))
    for index, paper in progress_bar:
        doi = paper["doi"]

        if doi != '':
            try:
                mendeley_paper = session.catalog.by_identifier(doi=doi)
            except mendeley.exception.MendeleyException:
                mendeley_paper = get_similar_paper(paper, session)
        else:
            mendeley_paper = get_similar_paper(paper, session)

        if mendeley_paper is not None:
            papers_details.loc[index, 'mendeley id'] = mendeley_paper.id
            papers_details.at[index, 'mendeley keywords'] = tuple(mendeley_paper.keywords) if mendeley_paper.keywords is not None else tuple()
            papers_details.at[index, 'publication ids'] = tuple(mendeley_paper.identifiers.items()) if mendeley_paper.identifiers is not None else None

    papers_details_mendeley_path = os.path.join('phase1_2', 'generated', 'papers_details.mendeley.csv')
    papers_details.drop_duplicates().to_csv(papers_details_mendeley_path)
    return papers_details_mendeley_path,


def get_similar_paper(paper, session):
    title = paper["title"]
    year = int(paper['year'])
    result = session.catalog.advanced_search(title=title, min_year=year, max_year=year)
    mendeley_paper: mendeley.models.catalog.CatalogDocument
    candidates = result.list().items
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        _logger.warning('more then one candidates found, return the first one')
        return candidates[0]
    else:
        _logger.warning('no candidates found')
        return None


if __name__ == '__main__':
    main(papers_details_path=os.path.join('phase1_2', 'generated', 'papers_details.csv'))
