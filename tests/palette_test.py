__author__ = 'milan'

import unittest
from PIL import Image
from cStringIO import StringIO

from google.appengine.ext import blobstore
from google.appengine.api import images

from timer import Timer
from lib import colorific
from models import Photo


def result(img):
    with Timer() as target:
        palette = colorific.extract_colors(img)
    print 'palette in %.2f ms' % target.elapsed
    print palette.bgcolor
    print palette.colors[0].value
    for c in palette.colors:
        print '%.2f %s' % (c.prominence, colorific.rgb_to_hex(c.value))


class PaletteTest(unittest.TestCase):
    def setUp(self):
        self.slug = 'fortis-flieger-cockpit-dark'

    def test_images_api(self):
        obj = Photo.get_by_id(self.slug)
        with Timer() as target:
            img = images.Image(blob_key=obj.blob_key)
            img.resize(width=100, height=100)
            thumb = img.execute_transforms(output_encoding=images.JPEG)  # str
            img = Image.open(StringIO(thumb))
        print 'image in %.2f ms' % target.elapsed
        result(img)

    def test_blobstore(self):
        obj = Photo.get_by_id(self.slug)
        with Timer() as target:
            blob_reader = blobstore.BlobReader(obj.blob_key)
            img = Image.open(StringIO(blob_reader.read()))
            thumb = img.resize((100, 100))
        print 'image in %.2f ms' % target.elapsed
        result(thumb)