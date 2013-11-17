from __future__ import division
__author__ = 'milan'

import unittest
import math
from models import Photo
from common import Paginator


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
        page, prev, obj, next = self.paginator.triple(1)
        self.assertEqual(page, 1)
        self.assertIsNone(prev)
        self.assertIsInstance(obj, Photo)
        self.assertIsInstance(next, Photo)

        page, prev1, obj1, next1 = self.paginator.triple(self.per_page)
        self.assertEqual(page, 1)
        self.assertIsInstance(prev1, Photo)
        self.assertIsInstance(obj1, Photo)
        self.assertIsInstance(next1, Photo)

        page, prev2, obj2, next2 = self.paginator.triple(self.per_page + 1)
        self.assertEqual(page, 2)
        self.assertEqual(prev2.key.string_id(), obj1.key.string_id())
        self.assertEqual(obj2.key.string_id(), next1.key.string_id())
        self.assertIsInstance(next, Photo)

        last_page = int(math.ceil(self.query.count() / self.per_page))
        page, prev3, obj3, next3 = self.paginator.triple(self.query.count())
        self.assertEqual(page, last_page)
        self.assertIsInstance(prev3, Photo)
        self.assertIsInstance(obj3, Photo)
        self.assertIsNone(next3)