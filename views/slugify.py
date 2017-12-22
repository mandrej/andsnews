# -*- coding: utf-8 -*-
import re
import unicodedata
MAPPINGS = {u'š': u's', u'č': u'c', u'ć': u'c', u'ž': u'z', u'dž': u'dz', u'đ': u'dj',
            u'а': u'a', u'б': u'b', u'в': u'v', u'г': u'g', u'д': u'd', u'ђ': u'dj', u'е': u'e',
            u'ж': u'z', u'з': u'z', u'и': u'i', u'ј': u'j', u'к': u'k', u'л': u'l', u'љ': u'lj',
            u'м': u'm', u'н': u'n', u'њ': u'nj', u'о': u'o', u'п': u'p', u'р': u'r', u'с': u's',
            u'т': u't', u'ћ': u'c', u'у': u'u', u'ф': u'f', u'х': u'h', u'ц': u'c', u'ч': u'c',
            u'џ': u'dz', u'ш': u's'}


def strip_punctuation(text):
    punctutation_cats = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
    return ''.join(x for x in text if unicodedata.category(x) not in punctutation_cats)

# https://pypi.python.org/pypi/re_transliterate/1.3
def word_replace(re_map, word):
    """Regex replace all occurrences of keys in re_map with their value."""
    for key, value in re_map.items():
        word = re.sub(key, value, word, flags=re.UNICODE)
    return word


def word_list_replace(re_map, words):
    """Apply word_replace to a list of words."""
    return [word_replace(re_map, word) for word in words]


def slugify(text):
    return '-'.join(word_list_replace(MAPPINGS, strip_punctuation(text).lower().split()))
