# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from candysorter.config import get_config
from candysorter.models import texts


if __name__ == '__main__':
    config = get_config('dev')

    text = 'I want chewy sweet chocolate'

    text_analyzer = texts.TextAnalyzer(config.WORD2VEC_MODEL_FILE)
    text_analyzer.init()

    labels = text_analyzer.labels
    tokens = text_analyzer.analyze_syntax(text)
    words = text_analyzer.filter_tokens(tokens)

    speech_similarities = text_analyzer.calc_similarities(words)
    print(speech_similarities)
