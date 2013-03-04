__author__ = 'milan'

import unittest
from colormath.color_objects import HSLColor


class ColorTest(unittest.TestCase):
    def test_spectra(self):
        data = []
        hue = {'red': 0, 'orange': 30, 'yellow': 60, 'green': 120, 'teal': 180, 'blue': 210, 'purple': 270, 'pink': 330}
        for name, h in hue.items():
            coll = []
            hue = h / 360.0
            for l in (10, 40,):
                lum = l / 100.0
                color = HSLColor(hue, 0.5, lum)
                rgb = color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
                coll.append(rgb)

            data.append({'name': name, 'colors': coll})

        print data

        # for lum in np.arange(0, 1.1, 0.1):
            # for sat in np.arange(0, 1.1, 0.1):
            #     color = HSLColor(0, sat, lum)
            #     # print color.get_value_tuple()
            #     print color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
            #     # print color.convert_to('lab').get_value_tuple()
