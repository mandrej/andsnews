__author__ = 'milan'

import unittest

def tokenize(phrase):
    a = []
    for word in phrase.split('-'):
        for i in range(1, len(word) + 1):
            a.append(word[:i])
    return a


class TimesinceTest(unittest.TestCase):
    def setUp(self):
        self.phrase = 'ivka-paradira-cipele'

    def test(self):
        print tokenize(self.phrase)