__author__ = 'milan'

import unittest
from models import Cloud, rounding
from config import CROPS, ASA, LENGTHS


class MiscTest(unittest.TestCase):
    def setUp(self):
        self.key = 'Photo_model'

    def test_crop_factor(self):
        cloud = Cloud(self.key).get_list()
        factors = list(set([CROPS[x.get('name')] for x in cloud]))
        factors.sort()
        words = map(str, factors)
        print words

    def test_round_iso(self):
        test = int(325)
        round = rounding(test, ASA)
        print 'Rounding {0} to {1}'.format(test, round)

    def test_round_eqv(self):
        test = int(45)
        round = rounding(test, LENGTHS)
        print 'Rounding {0} to {1}'.format(test, round)
