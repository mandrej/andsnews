from __future__ import division
__author__ = 'milan'

import unittest
import math
from models import Photo
from handlers import Paginator
from google.appengine.ext import ndb


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
        prev, obj, next = self.paginator.triple('ziveli-sokici')
        self.assertIsNone(prev)
        self.assertIsInstance(obj, Photo)
        self.assertIsInstance(next, Photo)

        prev, obj, next = self.paginator.triple('kia-rio-15-crdi')
        self.assertIsInstance(prev, Photo)
        self.assertIsInstance(obj, Photo)
        self.assertIsNone(next)