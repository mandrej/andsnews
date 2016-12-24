# -*- coding: utf-8 -*-
import unittest
from slugify import slugify
from models import tokenize


class TransliterateTest(unittest.TestCase):
    def test1(self):
        print slugify(u'Mišići')

    def test2(self):
        print slugify(u'Мишићи')

    def test3(self):
        print slugify(u'Ђоле с лоптом')

    def testTokenze(self):
        print tokenize('masa-gleda-u-tv-preko-knjige')
