__author__ = 'milan'

import unittest

class Paginator:

    def __init__(self, objects, per_page):
        self.objects = objects
        self.per_page = per_page
        self.count = len(objects)

    def page(self, num):
        offset = (num - 1)*self.per_page
        results = self.objects[offset: offset + self.per_page]
        has_next = self.count > len(self.objects[: offset + self.per_page])
        return results, has_next

    def tripleOLD(self, idx):
        """ num and idx are 1 base index """
        rem = idx%self.per_page
        num = int(idx/self.per_page) + (0 if rem == 0 else 1)
        objects, has_next = self.page(num)

        if rem == 1:
#            left edge
            if num == 1:
                if self.count == 1:
                    collection = [None] + objects + [None]
                else:
                    collection = [None] + objects
            else:
                other, x = self.page(num - 1)
                if idx == self.count:
                    collection = (other + objects + [None])[idx - (num - 2)*self.per_page - 2:]
                else:
                    collection = (other + objects)[idx - (num - 2)*self.per_page - 2:]
        elif rem == 0:
#            right edge
            if has_next:
                other, x = self.page(num + 1)
                collection = (objects + other)[idx - (num - 1)*self.per_page - 2:]
            else:
                collection = (objects + [None])[idx - (num - 1)*self.per_page - 2:]
        else:
            if idx == self.count:
                collection = (objects + [None])[idx - (num - 1)*self.per_page - 2:]
            else:
                collection = objects[idx - (num - 1)*self.per_page - 2:]

        return collection[:3]

    def triple(self, idx):
        """ num and idx are 1 base index """
        rem = idx%self.per_page
        num = int(idx/self.per_page) + (0 if rem == 0 else 1)
        objects, has_next = self.page(num)

        if rem == 1:
            if num == 1:
                other = [None]
            else:
                other, x = self.page(num - 1)
            collection = (other + objects + [None])[idx - (num - 2)*self.per_page - 2:]
        elif rem == 0:
            if has_next:
                other, x = self.page(num + 1)
            else:
                other = [None]
            collection = (objects + other)[idx - (num - 1)*self.per_page - 2:]
        else:
            collection = (objects + [None])[idx - (num - 1)*self.per_page - 2:]

        return collection[:3]

class PaginatorTest(unittest.TestCase):

    def test_page(self):
        paginator = Paginator(range(1, 27), 12)
        objects, has_next = paginator.page(1)
        self.assertEquals(objects, [1,2,3,4,5,6,7,8,9,10,11,12])
        self.assertTrue(has_next)

    def test_triple(self):
        paginator = Paginator(range(1, 27), 12)
        results = paginator.triple(13)
        self.assertEquals(results, [12,13,14])
