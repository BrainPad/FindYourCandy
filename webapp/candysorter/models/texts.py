# Copyright 2017 BrainPad Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import os

from gensim.models import Word2Vec
import numpy as np
from scipy import spatial

from candysorter.ext.google.cloud import language

logger = logging.getLogger(__name__)


class TextAnalyzer(object):
    _LANG_TO_NLAPI_LANG = {
        'en': 'en-US',
        'ja': 'ja',
    }

    def __init__(self, params_file, model_files, pos_weights):
        self.params_file = params_file
        self.model_files = model_files
        self.pos_weights = pos_weights

        self.labels = None
        self.models = None
        self.language_client = language.Client()

    @classmethod
    def from_config(cls, config):
        return cls(params_file=os.path.join(config['CLASSIFIER_MODEL_DIR'], 'params.json'),
                   model_files=config['WORD2VEC_MODEL_FILES'],
                   pos_weights=config['POS_WEIGHTS'])

    def init(self):
        self._load_models()
        self._load_labels()

    def reload(self):
        self._load_labels()

    def _load_models(self):
        self.models = {}
        for l, v in self.model_files.items():
            logger.info('Loading %s word2vec model...', l)
            self.models[l] = Word2Vec.load_word2vec_format(v['file'], binary=v['binary'])
            logger.info('Finished %s loading word2vec model.', l)

    def _load_labels(self):
        logger.info('Loading labels...')
        with open(self.params_file) as f:
            self.labels = json.load(f)['labels']
        logger.info('Finished loading labels.')

    def _to_nlapi_lang(self, lang):
        return self._LANG_TO_NLAPI_LANG.get(lang, 'en-US')

    def analyze_syntax(self, text, lang='en'):
        document = self.language_client.document_from_text(
            text, language=self._to_nlapi_lang(lang))
        return document.analyze_syntax()

    def calc_similarities(self, tokens, lang='en'):
        t_v = self._tokens_vector(tokens, lang)
        return np.array([
            1. - spatial.distance.cosine(t_v, l_v)
            for l_v in self._label_vectors(lang)
        ])

    def _tokens_vector(self, tokens, lang):
        model = self.models[lang]

        _tokens = [(t.lemma.lower(), t.pos.tag) for t in tokens]
        _tokens = [t for t in _tokens if t[0] in model]

        # no words
        if not _tokens:
            return (np.random.rand(model.vector_size) - 0.5) / model.vector_size

        # valid tokens
        valids = [t for t in _tokens if self._pos_weight(t[1]) > 0.]
        if valids:
            return sum([model[w] * self._pos_weight(p) for w, p in valids]) / len(valids)

        # all tokens
        return sum([model[w] for w, _ in _tokens]) / len(_tokens)

    def _label_vectors(self, lang):
        model = self.models[lang]

        vectors = []
        for l in self.labels:
            # e.g. 'SWEET CHOCOLATE' -> ['sweet', 'chocolate']
            words = [w.lower() for w in l.split(' ')]
            words = [w for w in words if w in model]
            if not words:
                v = (np.random.rand(model.vector_size) - 0.5) / model.vector_size
            else:
                v = sum([model[w] for w in words]) / len(words)
            vectors.append(v)
        return vectors

    def _pos_weight(self, pos):
        return self.pos_weights.get(pos, 0.)


class FakeTextAnalyzer(TextAnalyzer):
    def init(self):
        logger.info('*** %s loaded. ***', self.__class__.__name__)
        self._load_labels()

    def calc_similarities(self, words, lang='en'):
        return np.linspace(0.9, 0.1, len(self.labels))
