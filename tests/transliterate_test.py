# -*- coding: utf-8 -*-
import unittest
from views.slugify import slugify
from views.models import tokenize


class TransliterateTest(unittest.TestCase):
    def test1(self):
        print slugify(u'Mišići')

    def test2(self):
        print slugify(u'Gruja, Rumunija.')

    def test3(self):
        print slugify(u'Estação Olaias')

    def testTokenze(self):
        print tokenize('masa-gleda-u-tv-preko-knjige')
