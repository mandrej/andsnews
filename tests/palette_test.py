__author__ = 'milan'

import unittest
from lib import colorific


class PaletteTest(unittest.TestCase):
    def setUp(self):
        self.img = 'temp.jpg'

    def test_palette(self):
        pal = colorific.extract_colors(self.img)
        print pal
