__author__ = 'milan'

import unittest
from PIL import Image
from StringIO import StringIO
from google.appengine.api import images

from lib import colorific
from models import Photo


class PaletteTest(unittest.TestCase):
    def setUp(self):
        photo = Photo.get_by_id('motalica')
        img = images.Image(blob_key=photo.blob_key)
        img.resize(width=100, height=100)
        thumb = img.execute_transforms(output_encoding=images.JPEG)  # str
        self.img = Image.open(StringIO(thumb))

    def test_palette(self):
        pal = colorific.extract_colors(self.img)
        print pal.bgcolor
        # print pal.colors
        for c in pal.colors:
            print '%.2f %s' % (c.prominence, colorific.rgb_to_hex(c.value))
