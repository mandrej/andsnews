import unittest

from models import tokenize


class TimesinceTest(unittest.TestCase):
    def setUp(self):
        self.phrase = 'masa-gleda-u-tv-preko-knjige'

    def test(self):
        print tokenize(self.phrase)
