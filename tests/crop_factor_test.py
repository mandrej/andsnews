__author__ = 'milan'

import unittest
from models import Cloud
from config import CROPS


class CropFactorTest(unittest.TestCase):
    def setUp(self):
        self.key = 'Photo_model'

    def test_crop_factor(self):
        cloud = Cloud(self.key).get_list()
        factors = list(set([CROPS[x.get('name')] for x in cloud]))
        factors.sort()
        words = map(str, factors)
        print words
