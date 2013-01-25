__author__ = 'milan'

import math
import unittest

class Paginator:

    def __init__(self, objects, per_page):
        self.objects = objects
        self.per_page = per_page
        self.count = len(objects)
        self.num_pages = int(math.ceil(self.count/self.per_page)) + 1

    def page(self, num):
        offset = (num - 1)*self.per_page
        results = self.objects[offset: offset + self.per_page]
        has_next = self.count > len(self.objects[: offset + self.per_page])
        return results, has_next

    def triple(self, idx):
        """
        num and idx are 1 base index
        """
        collection = []
        rem = idx%self.per_page
        num = int(idx/self.per_page) + (0 if rem == 0 else 1)
        objects, has_next = self.page(num)
        print objects, has_next
        print '-------------------------', rem

        if rem == 1:
#            left edge
            if num == 1:
                if self.count == 1:
                    collection = [None] + objects + [None]
                    numbers = {'prev': None, 'next': None}
                else:
                    collection = [None] + objects
                    numbers = {'prev': None, 'next': idx + 1}
            else:
                if idx == self.count:
                    other, x = self.page(num - 1)
                    collection = (other + objects + [None])[idx - (num - 2)*self.per_page - 2:]
                    numbers = {'prev': idx - 1, 'next': None}
                else:
                    other, x = self.page(num - 1)
                    collection = (other + objects)[idx - (num - 2)*self.per_page - 2:]
                    numbers = {'prev': idx - 1, 'next': idx + 1}
        elif rem == 0:
#            right edge
            if has_next:
                other, x = self.page(num + 1)
                collection = (objects + other)[idx - (num - 1)*self.per_page - 2:]
                numbers = {'prev': idx - 1, 'next': idx + 1}
            else:
                collection = (objects + [None])[idx - (num - 1)*self.per_page - 2:]
                numbers = {'prev': idx - 1, 'next': None}
        else:
            if idx == self.count:
                collection = (objects + [None])[idx - (num - 1)*self.per_page - 2:]
                numbers = {'prev': idx - 1, 'next': None}
            else:
                collection = objects[idx - (num -1)*self.per_page - 2:]
                numbers = {'prev': idx - 1, 'next': idx + 1}

        return collection[:3], numbers

class PaginatorTest(unittest.TestCase):

    def setUp(self):
        self.paginator = Paginator(range(1, 26), 12)

    def tearDown(self):
        self.paginator = None

#    def test_page(self):
#        objects, has_next = self.paginator.page(1)
#        self.assertEquals(objects, [1,2,3,4,5,6,7,8,9,10,11,12])
#        self.assertTrue(has_next)

    def test_triple(self):
        self.paginator = Paginator(range(1, 27), 10)
        results, numbers = self.paginator.triple(21)
        print results, numbers