__author__ = 'milan'

import math
import unittest

class Paginator:

    def __init__(self, objects, per_page):
        self.objects = objects
        self.per_page = per_page

    def page(self, num):
        count = len(self.objects)
        num_pages = int(math.ceil(count/self.per_page)) + 1
        offset = (num - 1)*self.per_page
        results = self.objects[offset: offset + self.per_page]
        has_next = count > len(self.objects[: offset + self.per_page])
#        print 'num_pages %s' % num_pages
        return results, has_next

    def triple(self, page, idx):
        rem = idx%self.per_page
        print 'rem %s' % rem
        objects, has_next = self.page(page)
        print objects, has_next

        if page == 1 and rem == 1:
            collection = [None] + objects
            numbers = {'prev': None, 'next': idx + 1}
        elif page > 1 and rem == 1:
            other, has_next = self.page(page - 1)
            collection = (other + objects)[self.per_page + rem - 2:]
            numbers = {'prev': self.per_page, 'next': idx + 1}
        elif rem == 0:
            if has_next:
                other, has_next = self.page(page + 1)
                collection = (objects + other)[rem - 2:]
                numbers = {'prev': idx - 1, 'next': idx + 1}
            else:
                collection = objects[rem - 2:] + [None]
                numbers = {'prev': idx - 1, 'next': None}
        else:
            collection = objects[rem - 2:]
            numbers = {'prev': idx - 1, 'next': idx + 1}

        try:
            previous, obj, next = collection[:3]
        except ValueError:
            previous, obj = collection[:2]
            next = None

        return previous, obj, next, numbers

class PaginatorTest(unittest.TestCase):

    def setUp(self):
        self.paginator = Paginator(range(26), 12)

    def tearDown(self):
        self.paginator = None

#    def test_page(self):
#        objects, has_next = self.paginator.page(3)
#        print objects, has_next
#        self.assertTrue(has_next)

    def test_triple(self):
        previous, obj, next, numbers = self.paginator.triple(1, 3)
        print previous, obj, next
        print numbers