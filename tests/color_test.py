__author__ = 'milan'

import unittest
from colormath.color_objects import HSLColor
from models import Photo


class ColorTest(unittest.TestCase):
    def test_export(self):
        query = Photo.query()
        for obj in query:
            h, l, s = obj.hls
            color = HSLColor(h, s / 100.0, l / 100.0)
            values = color.get_value_tuple() + color.convert_to('lab').get_value_tuple()
            print('{0},{1},{2},{3},{4:.2f},{5:.2f},{6:.2f}'.format(obj.key.string_id(), *values))

        # for lum in np.arange(0, 1.1, 0.1):
            # for sat in np.arange(0, 1.1, 0.1):
            #     color = HSLColor(0, sat, lum)
            #     # print color.get_value_tuple()
            #     print color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
            #     # print color.convert_to('lab').get_value_tuple()
