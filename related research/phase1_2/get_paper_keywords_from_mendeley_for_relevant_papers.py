import logging
import os

import mendeley
import mendeley.models.catalog
import mendeley.exception
import pandas
import json

import varname

import util.log

logger = util.log.init_local_logger(logging.INFO)


def main():
    papers_details = pandas.read_csv(os.path.join('phase1_2', 'papers_details.csv'), index_col=0)
    papers_details['mendeley keywords'] = None
    papers_details['publication ids'] = None
    papers_details['mendeley keywords'] = papers_details['mendeley keywords'].astype('object')
    papers_details['publication ids'] = papers_details['publication ids'].astype('object')

    mendeley_client = mendeley.Mendeley(
        "10572",
        client_secret="egcetJherqDH0tJ5")

    auth = mendeley_client.start_client_credentials_flow()
    session = auth.authenticate()

    missings = []
    for index, paper in papers_details.iterrows():
        title = paper["title"]
        logger.info(f'looking for future data about {title}')
        doi = paper["doi"]

        mendeley_paper = None
        if doi != '':
            try:
                mendeley_paper = session.catalog.by_identifier(doi=doi)
            except mendeley.exception.MendeleyException:
                mendeley_paper = get_similar_paper(paper, session)
        else:
            mendeley_paper = get_similar_paper(paper, session)

        if mendeley_paper is None:
            missings.append(paper)
        else:
            papers_details.loc[index, 'mendeley id'] = mendeley_paper.id
            papers_details.at[index, 'mendeley keywords'] = tuple(mendeley_paper.keywords) if mendeley_paper.keywords is not None else tuple()
            papers_details.at[index, 'publication ids'] = tuple(mendeley_paper.identifiers.items()) if mendeley_paper.identifiers is not None else None

    papers_details.drop_duplicates().to_csv(os.path.join('phase1_2', varname.nameof(papers_details) + '.mendeley.csv'))


def get_similar_paper(paper, session):
    title = paper["title"]
    year = int(paper['year'])
    result = session.catalog.advanced_search(title=title, min_year=year, max_year=year)
    mendeley_paper: mendeley.models.catalog.CatalogDocument
    candidates = result.list().items
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        logger.warning('more then one candidates found, return the first one')
        return candidates[0]
    else:
        logger.warning('no candidates found')
        return None



if __name__ == '__main__':
    main()
