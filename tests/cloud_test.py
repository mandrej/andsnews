import unittest
from google.appengine.api import memcache
from timer import Timer
from operator import itemgetter
from models import Cloud


class CloudTest(unittest.TestCase):
    # def setUp(self):
    #     self.key = 'Photo_tags'
    #
    # def tearDown(self):
    #     memcache.delete(self.key)
    #     print ''
    #
    # def test_make(self):
    #     with Timer() as target:
    #         cloud = Cloud(self.key)
    #         coll = cloud.make()
    #     print coll
    #     # print cloud.get_list()
    #     print 'MAKE %s in %.2f ms' % (self.key, target.elapsed)
    #
    # def test_build(self):
    #     with Timer() as target:
    #         cloud = Cloud(self.key)
    #         coll = cloud.rebuild()
    #     print coll
    #     # print cloud.get_list()
    #     print 'BUILD %s in %.2f ms' % (self.key, target.elapsed)

    def test_reduce(self):
        # cloud = Cloud(self.key)
        cloud = [{'count': 1, 'name': u'aca', 'size': 1}, {'count': 90, 'name': u'ana', 'size': 7}, {'count': 64, 'name': u'architecture', 'size': 6}, {'count': 4, 'name': u'athens', 'size': 2}, {'count': 48, 'name': u'b&w', 'size': 6}, {'count': 6, 'name': u'barcelona', 'size': 3}, {'count': 89, 'name': u'belgrade', 'size': 7}, {'count': 1, 'name': u'brownie', 'size': 1}, {'count': 5, 'name': u'budapest', 'size': 3}, {'count': 6, 'name': u'bugs', 'size': 3}, {'count': 1, 'name': u'dimitrije', 'size': 1}, {'count': 258, 'name': u'djordje', 'size': 8}, {'count': 5, 'name': u'dubrovnik', 'size': 3}, {'count': 13, 'name': u'dusan', 'size': 4}, {'count': 1, 'name': u'espresso', 'size': 1}, {'count': 12, 'name': u'event', 'size': 4}, {'count': 1, 'name': u'filip', 'size': 1}, {'count': 11, 'name': u'flowers', 'size': 4}, {'count': 39, 'name': u'food', 'size': 6}, {'count': 5, 'name': u'hdr', 'size': 3}, {'count': 29, 'name': u'home', 'size': 5}, {'count': 2, 'name': u'ines', 'size': 1}, {'count': 7, 'name': u'istanbul', 'size': 3}, {'count': 294, 'name': u'iva', 'size': 8}, {'count': 2, 'name': u'jelena', 'size': 1}, {'count': 140, 'name': u'katarina', 'size': 7}, {'count': 5, 'name': u'kia', 'size': 3}, {'count': 7, 'name': u'kotor', 'size': 3}, {'count': 55, 'name': u'landscape', 'size': 6}, {'count': 10, 'name': u'las vegas', 'size': 4}, {'count': 1, 'name': u'laza', 'size': 1}, {'count': 57, 'name': u'lisbon', 'size': 6}, {'count': 25, 'name': u'macro', 'size': 5}, {'count': 183, 'name': u'masa', 'size': 8}, {'count': 160, 'name': u'mihailo', 'size': 8}, {'count': 1, 'name': u'mikan', 'size': 1}, {'count': 86, 'name': u'milan', 'size': 7}, {'count': 20, 'name': u'milos', 'size': 5}, {'count': 4, 'name': u'mladen', 'size': 2}, {'count': 46, 'name': u'montenegro', 'size': 6}, {'count': 2, 'name': u'neda', 'size': 1}, {'count': 4, 'name': u'nemanja', 'size': 2}, {'count': 62, 'name': u'night', 'size': 6}, {'count': 2, 'name': u'nina', 'size': 1}, {'count': 242, 'name': u'portrait', 'size': 8}, {'count': 7, 'name': u'roma', 'size': 3}, {'count': 1, 'name': u'sara', 'size': 1}, {'count': 33, 'name': u'ski', 'size': 5}, {'count': 30, 'name': u'sky', 'size': 5}, {'count': 3, 'name': u'sladja', 'size': 2}, {'count': 3, 'name': u'slavica', 'size': 2}, {'count': 1, 'name': u'slobodanka', 'size': 1}, {'count': 2, 'name': u'sofija', 'size': 1}, {'count': 8, 'name': u'sombor', 'size': 3}, {'count': 2, 'name': u'sonja', 'size': 1}, {'count': 1, 'name': u'stefan', 'size': 1}, {'count': 143, 'name': u'still life', 'size': 7}, {'count': 3, 'name': u'stokholm', 'size': 2}, {'count': 94, 'name': u'svetlana', 'size': 7}, {'count': 17, 'name': u'tara', 'size': 4}, {'count': 1, 'name': u'timisoara', 'size': 1}, {'count': 1, 'name': u'triggertrap', 'size': 1}, {'count': 7, 'name': u'ugljesa', 'size': 3}, {'count': 49, 'name': u'urban', 'size': 6}, {'count': 1, 'name': u'uros', 'size': 1}, {'count': 2, 'name': u'vanja', 'size': 1}, {'count': 4, 'name': u'venezia', 'size': 2}, {'count': 35, 'name': u'water', 'size': 5}, {'count': 30, 'name': u'wedding', 'size': 5}, {'count': 12, 'name': u'wien', 'size': 4}]
        cloud_on_count = sorted(cloud, key=itemgetter('count'))
        sum5 = sum((x['count'] for x in cloud)) * 0.05
        curr = 0
        limit = 0
        for item in cloud_on_count:
            curr += item['count']
            if curr >= sum5:
                print curr
                limit = item['count']
                break

        print sum5
        print limit
