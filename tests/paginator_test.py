from __future__ import division

import unittest
import math

from views.models import Photo
# from handlers import Paginator
# from config import PHOTOS_PER_PAGE


# class PaginatorTest(unittest.TestCase):
    # def setUp(self):
    #     self.query = Photo.query().order(-Photo.date)
    #     self.paginator = Paginator(self.query, per_page=PHOTOS_PER_PAGE)
    #     self.per_page = self.paginator.per_page
    #
    # def test_page(self):
    #     objects, has_next = self.paginator.page(1)
    #     self.assertEqual(len(objects), self.per_page)
    #     self.assertTrue(has_next)
    #
    #     last_page = int(math.ceil(self.query.count() / self.per_page))
    #     objects, has_next = self.paginator.page(last_page)
    #     self.assertEqual(len(objects), self.query.count() - self.per_page * (last_page - 1))
    #     self.assertFalse(has_next)
    #
    # def test_triple(self):
    #     page, prev, obj, next = self.paginator.triple('zenith-velibora-andrejevica')
    #     self.assertEqual(page, 1)
    #     self.assertIsNone(prev)
    #     self.assertIsInstance(obj, Photo)
    #     self.assertIsInstance(next, Photo)
    #
    #     page, prev, obj, next = self.paginator.triple('manastir-dudovica')
    #     self.assertEqual(page, 1)
    #     self.assertIsInstance(prev, Photo)
    #     self.assertIsInstance(obj, Photo)
    #     self.assertIsInstance(next, Photo)
    #
    #     page, prev, obj, next = self.paginator.triple('kia-rio-15-crdi')
    #     self.assertEqual(page, 2)
    #     self.assertIsInstance(prev, Photo)
    #     self.assertIsInstance(obj, Photo)
    #     self.assertIsNone(next)
    #
    # def test_neighbors(self):
    #     index, objects, next_more, next_cursor, prev_more, prev_cursor = self.paginator.neighbors('fortis-flieger-cockpit')
    #     print index
    #     print next_more
    #     print next_cursor
    #     print prev_more
    #     print prev_cursor
    #     j = 0
    #     for x in objects:
    #         print j, x.key.string_id()
    #         j += 1
