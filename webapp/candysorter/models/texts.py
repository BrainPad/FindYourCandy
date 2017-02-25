# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import os

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

    def __init__(self, params_file, model_file):
        self.params_file = params_file
        self.model_file = model_file

        self.labels = None
        self.model = None
        self.language_client = language.Client()

    @classmethod
    def from_config(cls, config):
        return cls(params_file=os.path.join(config.CLASSIFIER_MODEL_DIR, 'params.json'),
                   model_file=config.WORD2VEC_MODEL_FILE)

    def init(self):
        self._load_model()
        self._load_labels()

    def reload(self):
        self._load_labels()

    def _load_model(self):
        logger.info('Loading word2vec model...')
        self.model = gensim.models.Word2Vec.load_word2vec_format(self.model_file, binary=True)
        logger.info('Finished loading word2vec model.')

    def _load_labels(self):
        logger.info('Loading labels...')
        with open(self.params_file) as f:
            self.labels = json.load(f)['labels']
        logger.info('Finished loading labels.')

    def analyze_syntax(self, text, language=language.DEFAULT_LANGUAGE):
        document = self.language_client.document_from_text(text, language=language)
        return document.analyze_syntax()

    def filter_tokens(self, tokens):
        return [t.lemma for t in tokens if t.pos.tag in self._PARTS_OF_SPEECH]

    def calc_similarities(self, words):
        # TODO: multi words per label
        words = map(lambda w_: w_.lower(), words)
        words = filter(lambda w_: w_ in self.model, words)
        avg_v = sum([self.model[w] for w in words]) / len(words)
        return np.array([
            1. - spatial.distance.cosine(avg_v, l_v)
            for l_v in self._label_vectors()
        ])

    def _label_vectors(self):
        vectors = []
        for l in self.labels:
            # e.g. 'SWEET CHOCOLATE' -> ['sweet', 'chocolate']
            words = [w.lower() for w in l.split(' ')]
            words = [w for w in words if w in self.model]
            if not words:
                v = (np.random.rand(self.model.vector_size) - 0.5) / self.model.vector_size
            else:
                v = sum([self.model[w] for w in words]) / len(words)
            vectors.append(v)
        return vectors


class FakeTextAnalyzer(TextAnalyzer):
    def init(self):
        logger.info('*** %s loaded. ***', self.__class__.__name__)
        self._load_labels()

    def calc_similarities(self, words):
        return np.linspace(0.9, 0.1, len(self.labels))
