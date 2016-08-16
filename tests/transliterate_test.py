# -*- coding: utf-8 -*-
import unittest
from slugify import slugify


class TransliterateTest(unittest.TestCase):
    def test1(self):
        print slugify(u'Mišići')

    def test2(self):
        print slugify(u'Мишићи')

    def test3(self):
        print slugify(u'Misici')
