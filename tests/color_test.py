__author__ = 'milan'

import unittest
from colormath.color_objects import HSLColor, SpectralColor


class ColorTest(unittest.TestCase):
    def test_spectra(self):
        print 'RED'
        c = SpectralColor(440)  # .get_numpy_array().convert_to('xyz')
        print c.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
        print  c
        # print SpectralColor('spec_760nm').get_numpy_array()
        # print SpectralColor('spec_760nm').convert_to('hsl').get_numpy_array()

        # print data

        # for lum in np.arange(0, 1.1, 0.1):
            # for sat in np.arange(0, 1.1, 0.1):
            #     color = HSLColor(0, sat, lum)
            #     # print color.get_value_tuple()
            #     print color.convert_to('rgb', target_rgb='sRGB').get_rgb_hex()
            #     # print color.convert_to('lab').get_value_tuple()
