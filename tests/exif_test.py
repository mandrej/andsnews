import unittest
from cStringIO import StringIO

from exifread import process_file
from models import Photo
from timer import Timer


class ExifTest(unittest.TestCase):
    def test_exif(self):
        obj = Photo.get_by_id('mirodjija')
        with Timer() as target:
            tags = process_file(StringIO(obj.buffer), details=False)
        print 'Done in %.2f ms' % target.elapsed
        for k, v in tags.items():
            print '%s\t\t%s' % (k, v.printable)
