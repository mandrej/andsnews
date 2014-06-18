__author__ = 'milan'

import unittest
from google.appengine.ext import ndb
from models import Photo
from timer import Timer


class WakTest(unittest.TestCase):
    def setUp(self):
        self.key = ndb.Key('Photo', 'ziveli-sokici')
        self.query = Photo.query().order(-Photo.date)

    def test_iter(self):
        i = self.query.iter(keys_only=True)
        # print i.index_list()
        with Timer() as target:
            li = [x for x in i]
        idx = li.index(self.key)
        print 'ITER Found index %s in %.2f ms' % (idx, target.elapsed)

    def test_fetch(self):
        with Timer() as target:
            li = self.query.fetch(keys_only=True)
        idx = li.index(self.key)
        print 'FETCH Found index %s in %.2f ms' % (idx, target.elapsed)
