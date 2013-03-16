__author__ = 'milan'

import unittest
from google.appengine.api import memcache
from timer import Timer
from models import make_cloud, count_property


class CloudTest(unittest.TestCase):
    def setUp(self):
        self.key = 'Photo_color'

    def tearDown(self):
        memcache.delete(self.key)
        print ''

    def test_make(self):
        with Timer() as target:
            content = make_cloud(self.key)
        print content
        print 'MAKE %s in %.2f ms' % (self.key, target.elapsed)

    def test_build(self):
        with Timer() as target:
            content = count_property(self.key)
        print content
        print 'BUILD %s in %.2f ms' % (self.key, target.elapsed)