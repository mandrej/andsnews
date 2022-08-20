import unittest
import json
import itertools
import functools
import collections
from .photo import datastore_client


class TestApp(unittest.TestCase):
    def setUp(self):
        self.field = 'tags'
        self.query = datastore_client.query(kind='Photo')

    def test_data(self):
        iter_ = self.query.fetch()
        if self.field == 'tags':
            values = [item for ent in iter_ for item in ent[self.field]]
        else:
            values = [ent[self.field] for ent in iter_ if ent[self.field]]

        tally = collections.Counter(values)
        print(tally)
        # query = datastore_client.query(kind='Photo', order=['-date'])
        # res = [x['tags'] for x in query.fetch()]

        # flat = functools.reduce(lambda x, y: x + y, res)

        # tally = {}
        # for name in flat:
        #     if name in tally:
        #         tally[name] += 1
        #     else:
        #         tally[name] = 1

        # i = 0
        # nodes = []
        # items = {}
        # for name, count in tally.items():
        #     items[name] = i
        #     nodes.append({'name': name, 'index': i, 'count': count})
        #     i += 1

        # links = []
        # pairs = itertools.combinations(items.keys(), 2)
        # for x, y in pairs:
        #     i = 0
        #     for tags in res:
        #         # set literals back-ported from Python 3.x
        #         intersection = set(tags) & {x, y}
        #         i += intersection == {x, y}
        #     if i > 0:
        #         links.append(
        #             {'source': items[x], 'target': items[y], 'value': i})

        # collection = json.dumps({'nodes': nodes, 'links': links})
        # print(collection)


# no need to run server!
# (andsnews) $ python -m unittest api/test_rebuild.py
