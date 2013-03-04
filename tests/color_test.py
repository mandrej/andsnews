__author__ = 'milan'

import unittest
import numpy as np
from colormath.color_objects import HSLColor
from settings import HUE, LUM, SAT


class ColorTest(unittest.TestCase):
    def test_spectar(self):
        res = []
        for H in HUE:
            # print H['name']
            for h in (0, 25, 50, 105, 170, 215, 265, 320,):
                hue = h / 360.0
                for L in  LUM:
                    # print L['name']
                    for l in (10, 40,):
                        lum = l / 100.0
                        # res['%s_%s' % (H['name'], L['name'])] = []
                        for S in SAT:
                            # print '%s_%s_%s' % (H['name'], L['name'], S['name'])
                            # print S['name']
                            for s in (20,):
                                sat = s / 100.0
                                color = HSLColor(hue, sat, lum)
                                rgb = color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
                                res.append(rgb)
                                print rgb

        print res


        # for lum in np.arange(0, 1.1, 0.1):
            # for sat in np.arange(0, 1.1, 0.1):
            #     color = HSLColor(0, sat, lum)
            #     # print color.get_value_tuple()
            #     print color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
            #     # print color.convert_to('lab').get_value_tuple()
