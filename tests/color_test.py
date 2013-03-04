__author__ = 'milan'

import unittest
from colormath.color_objects import HSLColor
from settings import HUE


class ColorTest(unittest.TestCase):
    def test_spectra(self):
        res = {}
        for H in HUE:
            res[H['name']] = []
            for h in (0, 25, 50, 105, 170, 215, 265, 320,):
                hue = h / 360.0
                for l in (10, 40,):
                    lum = l / 100.0
                    for s in (50,):
                        sat = s / 100.0
                        color = HSLColor(hue, sat, lum)
                        rgb = color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
                        res[H['name']].append(rgb)

        print res

        # for lum in np.arange(0, 1.1, 0.1):
            # for sat in np.arange(0, 1.1, 0.1):
            #     color = HSLColor(0, sat, lum)
            #     # print color.get_value_tuple()
            #     print color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
            #     # print color.convert_to('lab').get_value_tuple()
