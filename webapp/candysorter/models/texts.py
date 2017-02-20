# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import gensim
import numpy as np
from scipy import spatial

from candysorter.ext.google.cloud import language

logger = logging.getLogger(__name__)


class TextAnalyzer(object):
    _PARTS_OF_SPEECH = set([
        language.PartOfSpeech.ADJECTIVE,
        language.PartOfSpeech.NOUN,
    ])

    def __init__(self, model_file):
        self.model = None
        self.model_file = model_file
        self.language_client = language.Client()

    @classmethod
    def from_config(cls, config):
        return cls(model_file=config.WORD2VEC_MODEL_FILE)

    def init(self):
        logger.info('Loading word2vec model...')
        # TODO: too slow
        self.model = gensim.models.Word2Vec.load_word2vec_format(self.model_file, binary=True)
        logger.info('Finished loading word2vec model.')

        # TODO: from global database
        logger.info('Getting labels...')
        self.labels = ['CHOCOLATE', 'COOKIE', 'MINT', 'SOUR']
        logger.info('Finished getting labels.')

    def analyze_syntax(self, text):
        document = self.language_client.document_from_text(text, language='en-US')  # TODO: i18n
        return document.analyze_syntax()

    def filter_tokens(self, tokens):
        return [t.lemma for t in tokens if t.pos.tag in self._PARTS_OF_SPEECH]

    def calc_similarities(self, words):
        # TODO: distance -> similarity
        avg_v = sum([self.model[w] for w in words]) / len(words)
        return np.array([1. - spatial.distance.cosine(avg_v, self.model[l]) for l in self.labels])


class FakeTextAnalyzer(TextAnalyzer):
    def init(self):
        self.labels = ['CHOCOLATE', 'COOKIE', 'MINT', 'SOUR']

    def calc_similarities(self, words):
        return np.linspace(0.9, 0.1, len(self.labels))
