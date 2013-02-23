__author__ = 'milan'

import unittest

from google.appengine.api import memcache

from timer import Timer

from common import make_cloud, count_property


class CloudTest(unittest.TestCase):
    def setUp(self):
        self.key = 'Photo_date'
        self.kind, self.field = self.key.split('_')

    def tearDown(self):
        memcache.delete(self.key)
        print 'clear memcache'

    def test_make(self):
        with Timer() as target:
            self.failUnless(make_cloud(self.kind, self.field))
        print 'make %s in %.2f ms' % (self.key, target.elapsed)

    def test_build(self):
        with Timer() as target:
            self.failUnless(count_property(self.kind, self.field))
        print 'build %s in %.2f ms' % (self.key, target.elapsed)