# -*- coding: utf-8 -*-
import unittest
from views.models import slugify, tokenize


class TransliterateTest(unittest.TestCase):
    def test1(self):
        print slugify(u'Mišići Чањ, Црна Гора. Комшилук')

    def test2(self):
        print slugify(u'Gruja, Rumunija. Божићна звезда')

    def test3(self):
        print slugify(u'Estação Olaias')

    def testTokenze(self):
        print tokenize('misici-chanj-tsrna-gora-komshiluk')
