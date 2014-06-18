from __future__ import division
__author__ = 'milan'

import unittest
import math
from models import Photo
from handlers import Paginator


class PaginatorTest(unittest.TestCase):
    def setUp(self):
        self.query = Photo.query().order(-Photo.date)
        self.paginator = Paginator(self.query)
        self.per_page = self.paginator.per_page

    def test_page(self):
        objects, has_next = self.paginator.page(1)
        self.assertEqual(len(objects), self.per_page)
        self.assertTrue(has_next)

        last_page = int(math.ceil(self.query.count() / self.per_page))
        objects, has_next = self.paginator.page(last_page)
        self.assertEqual(len(objects), self.query.count() - self.per_page * (last_page - 1))
        self.assertFalse(has_next)

    def test_triple(self):
        page, prev, obj, next = self.paginator.triple('ziveli-sokici')
        self.assertEqual(page, 1)
        self.assertIsNone(prev)
        self.assertIsInstance(obj, Photo)
        self.assertIsInstance(next, Photo)

        page, prev, obj, next = self.paginator.triple('gruja-rumunija')
        self.assertEqual(page, 1)
        self.assertIsInstance(prev, Photo)
        self.assertIsInstance(obj, Photo)
        self.assertIsInstance(next, Photo)

        page, prev, obj, next = self.paginator.triple('nasa-deca')
        self.assertEqual(page, 2)
        self.assertIsInstance(prev, Photo)
        self.assertIsInstance(obj, Photo)
        self.assertIsInstance(next, Photo)

"""
from models import Photo
query = Photo.query().order(-Photo.date)
i = query.iter(produce_cursors=True)
for x in i:
  before = i.cursor_before()
  #after = i.cursor_after()
  #print before.urlsafe()
  #print after.urlsafe()

  num = 3 if before.urlsafe() else 2
  results, cursor, has_next = query.fetch_page(num, start_cursor=before.reversed())
  for p in results:
    print p.key
  #print cursor.urlsafe()
  print '---------------------------'
"""