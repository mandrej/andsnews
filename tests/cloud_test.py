__author__ = 'milan'

import unittest
from google.appengine.api import memcache
from timer import Timer
from models import Cloud


class CloudTest(unittest.TestCase):
    def setUp(self):
        self.key = 'Photo_iso'

    def tearDown(self):
        memcache.delete(self.key)
        print ''

    def test_make(self):
        with Timer() as target:
            cloud = Cloud(self.key)
            coll = cloud.make()
        print coll
        # print cloud.get_list()
        print 'MAKE %s in %.2f ms' % (self.key, target.elapsed)

    def test_build(self):
        with Timer() as target:
            cloud = Cloud(self.key)
            coll = cloud.rebuild()
        print coll
        # print cloud.get_list()
        print 'BUILD %s in %.2f ms' % (self.key, target.elapsed)