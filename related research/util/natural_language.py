import re
from typing import List

import nltk
from nltk.corpus import wordnet

stop_words = set(nltk.corpus.stopwords.words('english'))


def drop_stop_words(tokens: List[str]):
    return [word for word in tokens if not word.lower() in stop_words]


def drop_non_alpha(tokens: List[str]):
    return [word for word in tokens if not re.search(r'[\W0-9]', word)]


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def lemmatize(tokens):
    tokens = tuple(map(str.lower, tokens))
    stemmer = nltk.stem.WordNetLemmatizer()
    cleared_tokens = drop_non_alpha(drop_stop_words(tokens))
    pos_tokens = [pos_tagged for pos_tagged in nltk.pos_tag(tokens) if pos_tagged[0] in cleared_tokens]
    wordnet_pos_tokens = [(token, get_wordnet_pos(pos), pos) for token, pos in pos_tokens if
                          get_wordnet_pos(pos) is not None]
    lemmas = [(stemmer.lemmatize(token, pos=wordnet_pos), treebank_pos) for token, wordnet_pos, treebank_pos in
              wordnet_pos_tokens]
    return lemmas