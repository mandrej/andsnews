import unittest

from models import rounding
from config import ASA


class MiscTest(unittest.TestCase):
    def setUp(self):
        self.key = 'Photo_model'

    def test_round_iso(self):
        test = int(325)
        round = rounding(test, ASA)
        print 'Rounding {0} to {1}'.format(test, round)
