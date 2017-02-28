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

from google.cloud import language

DEFAULT_LANGUAGE = language.document.DEFAULT_LANGUAGE


class Client(language.Client):
    def document_from_text(self, content, **kwargs):
        if 'doc_type' in kwargs:
            raise TypeError('Cannot pass doc_type')
        return Document(self, content=content, doc_type=language.Document.PLAIN_TEXT, **kwargs)


class Document(language.Document):
    def analyze_syntax(self):
        data = {
            'document': self._to_dict(),
            'encodingType': self.encoding,
        }
        api_response = self.client._connection.api_request(
            method='POST', path='analyzeSyntax', data=data)
        return [Token.from_api_repr(token) for token in api_response.get('tokens', ())]


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


class PartOfSpeech(language.syntax.PartOfSpeech):
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
