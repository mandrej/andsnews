import unittest
import collections

import numpy as np

from colormath.color_objects import HSLColor, sRGBColor
from colormath.color_conversions import convert_color
from models import Photo
from config import HUE


class ColorTest(unittest.TestCase):
    def test_export(self):
        query = Photo.query()
        for obj in query:
            h, l, s = obj.hls
            color = HSLColor(h, s / 100.0, l / 100.0)
            values = color.get_value_tuple()
            print '{0},{1},{2},{3}'.format(obj.key.string_id(), *values)

    def test_mean(self):
        colors = []
        query = Photo.query()
        for obj in query:
            color = sRGBColor(*obj.rgb)
            colors.append(convert_color(color, HSLColor).get_value_tuple())

        print 'HUE mean {0:.2f}\nSAT mean {1:.2f}\nLUM mean {2:.2f}'.format(*tuple(np.mean(colors, axis=0)))
        print
        print 'HUE std {0:.2f}\nSAT std {1:.2f}\nLUM std {2:.2f}'.format(*tuple(np.std(colors, axis=0)))

    def test_spectra(self):
        sat = 10  # int(self.request.get('sat', 20))
        lum = 40  # int(self.request.get('lum', 40))
        spectra = collections.OrderedDict()
        for row in HUE:
            temp = []
            for hue in row['span']:
                color = HSLColor(hue, sat / 100.0, lum / 100.0)
                hsl = 'hsl({0}, {1:.0%}, {2:.0%})'.format(*color.get_value_tuple())
                temp.append(hsl)
            spectra[row['name']] = temp

        print spectra