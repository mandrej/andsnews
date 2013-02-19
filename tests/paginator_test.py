__author__ = 'milan'

import unittest
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

        objects, has_next = self.paginator.page(5)
        self.assertEqual(len(objects), 0)
        self.assertFalse(has_next)

    def test_triple(self):
        page, prev, obj, next = self.paginator.triple(1)
        self.assertEqual(page, 1)
        self.assertIsNone(prev)
        self.assertIsInstance(obj, Photo)
        self.assertIsInstance(next, Photo)

        page, prev1, obj1, next1 = self.paginator.triple(self.per_page)
        #            prev2, obj2, next2
        self.assertEqual(page, 1)
        self.assertIsInstance(prev1, Photo)
        self.assertIsInstance(obj1, Photo)
        self.assertIsInstance(next1, Photo)

        page, prev2, obj2, next2 = self.paginator.triple(self.per_page + 1)
        self.assertEqual(page, 2)
        self.assertEqual(prev2.key.string_id(), obj1.key.string_id())
        self.assertEqual(obj2.key.string_id(), next1.key.string_id())
        self.assertIsInstance(next, Photo)

        page, prev, obj, next = self.paginator.triple(self.query.count())
        self.assertEqual(page, 3)
        self.assertIsInstance(prev, Photo)
        self.assertIsInstance(obj, Photo)
        self.assertIsNone(next)