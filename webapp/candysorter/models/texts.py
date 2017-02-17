# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import gensim
from google.cloud import language
import numpy as np
from scipy import spatial

logger = logging.getLogger(__name__)


class Token(object):
    def __init__(self, text, pos, dep, lemma):
        self.text = text
        self.pos = pos
        self.dep = dep
        self.lemma = lemma

    @classmethod
    def from_api_repr(cls, payload):
        return cls(TextSpan.from_api_repr(payload['text']),
                   PartOfSpeech.from_api_repr(payload['partOfSpeech']),
                   DependencyEdge.from_api_repr(payload['dependencyEdge']),
                   payload['lemma'])


class TextSpan(object):
    def __init__(self, content, offset):
        self.content = content
        self.offset = offset

    @classmethod
    def from_api_repr(cls, payload):
        return cls(payload['content'], payload['beginOffset'])


class PartOfSpeech(object):
    def __init__(self, tag, aspect, case, form, gender, mood, number, person, proper, reciprocity,
                 tense, voice):
        self.tag = tag
        self.aspect = aspect
        self.case = case
        self.form = form
        self.gender = gender
        self.mood = mood
        self.number = number
        self.person = person
        self.proper = proper
        self.reciprocity = reciprocity
        self.tense = tense
        self.voice = voice

    @classmethod
    def from_api_repr(cls, payload):
        return cls(payload['tag'], payload['aspect'], payload['case'], payload['form'],
                   payload['gender'], payload['mood'], payload['number'], payload['person'],
                   payload['proper'], payload['reciprocity'], payload['tense'], payload['voice'])


class DependencyEdge(object):
    def __init__(self, index, label):
        self.index = index
        self.label = label

    @classmethod
    def from_api_repr(cls, payload):
        return cls(payload['headTokenIndex'], payload['label'])


class TextAnalyzer(object):
    _PARTS_OF_SPEECH = set([
        language.syntax.PartOfSpeech.ADJECTIVE,
        language.syntax.PartOfSpeech.NOUN,
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
        self.labels = ['creamy', 'sour', 'sweet']
        logger.info('Finished getting labels.')

    def analyze_syntax(self, text):
        data = {
            'document': {
                'type': language.Document.PLAIN_TEXT,
                'language': 'en-US',
                'content': text,

            },
            'encodingType': language.Encoding.UTF8,
        }
        res = self.language_client._connection.api_request(
            method='POST', path='analyzeSyntax', data=data
        )
        return [Token.from_api_repr(t) for t in res.get('tokens', [])]

    def filter_tokens(self, tokens):
        return [t.lemma for t in tokens if t.pos.tag in self._PARTS_OF_SPEECH]

    def calc_similarities(self, words):
        # TODO: distance -> similarity
        avg_v = sum([self.model[w] for w in words]) / len(words)
        return np.array([spatial.distance.cosine(avg_v, self.model[l]) for l in self.labels])


class FakeTextAnalyzer(TextAnalyzer):
    def init(self):
        self.labels = ['creamy', 'sour', 'sweet']

    def calc_similarities(self, words):
        return np.linspace(0.9, 0.1, len(self.labels))
