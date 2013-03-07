__author__ = 'milan'

import unittest
from colormath.color_objects import HSLColor
from models import Photo
from collections import defaultdict
from settings import HUE


class ColorTest(unittest.TestCase):
    def test_export(self):
        query = Photo.query()
        for obj in query:
            h, l, s = obj.hls
            color = HSLColor(h, s / 100.0, l / 100.0)
            values = color.get_value_tuple() + color.convert_to('lab').get_value_tuple()
            print('{0},{1},{2},{3},{4:.2f},{5:.2f},{6:.2f}'.format(obj.key.string_id(), *values))

    def test_spectra(self):

        spectra = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for sat in (20, 60,):
            for lum in (40, 80,):
                for row in HUE:
                    for hue in row['span']:
                        color = HSLColor(hue, sat / 100.0, lum / 100.0)
                        rgb = color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
                        spectra[sat][lum][row['name']].append(rgb)

        for sat, x in spectra.items():
            print sat
            for lum, y in x.items():
                print('\t{0}\n{1}'.format(lum, y))

