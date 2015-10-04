import unittest
import urllib
from cStringIO import StringIO

from PIL import Image
from google.appengine.ext import blobstore
from google.appengine.api import images

from timer import Timer
from palette import extract_colors, rgb_to_hex
from models import Photo


def result(img):
    with Timer() as target:
        palette = extract_colors(img)
    print 'palette in %.2f ms' % target.elapsed
    print palette.bgcolor
    print palette.colors[0].value
    for c in palette.colors:
        print '%.2f %s' % (c.prominence, rgb_to_hex(c.value))


class PaletteTest(unittest.TestCase):
    def setUp(self):
        obj = Photo.get_by_id('red')
        blob_reader = blobstore.BlobReader(obj.blob_key, buffer_size=1024*1024)
        self.buff = blob_reader.read(size=-1)
        self.url = images.get_serving_url(obj.blob_key, size=300, crop=True, secure_url=True)

    def test_images_api(self):
        with Timer() as target:
            img = images.Image(self.buff)
            img.resize(width=100, height=100)
            thumb = img.execute_transforms(output_encoding=images.JPEG, quality=86)  # str
        print 'API image in %.2f ms' % target.elapsed
        result(StringIO(thumb))

    def test_blobstore(self):
        with Timer() as target:
            img = Image.open(StringIO(self.buff))
            img.thumbnail((100, 100), Image.ANTIALIAS)
            # output = StringIO()
            # img.save(output, format='JPEG')
            # thumb = output.getvalue()
            # output.close()
        print 'PIL image in %.2f ms' % target.elapsed
        result(img)

    def test_from_url(self):
        with Timer() as target:
            file = StringIO(urllib.urlopen(self.url).read())
            img = Image.open(file)
        print 'PIL image from url %.2f ms' % target.elapsed
        result(img)