import unittest
import json
import itertools
import functools
from .photo import datastore_client


class TestApp(unittest.TestCase):
    def setUp(self):
        self.family = ['milan', 'svetlana', 'ana', 'mihailo', 'milos', 'katarina', 'iva', 'masa', 'djordje', 'bogdan']
    
    def test_data(self):
        # res = []
        # for member in self.family:
        #     query = datastore_client.query(kind='Photo')
        #     query.add_filter(*('tags', '=', member))
        #     res += [x['tags'] for x in query.fetch()]
        query = datastore_client.query(kind='Photo', order=['-date'])
        res = [x['tags'] for x in query.fetch()]
        
        flat = functools.reduce(lambda x, y: x + y, res)

        tally = {}
        for name in flat:
            if name in tally:
                tally[name] += 1
            else:
                tally[name] = 1
        
        i = 0
        nodes = []
        items = {}
        for name, count in tally.items():
            items[name] = i
            nodes.append({'name': name, 'index': i, 'count': count})
            i += 1
        
        links = []
        pairs = itertools.combinations(items.keys(), 2)
        for x, y in pairs:
            i = 0
            for tags in res:
                # set literals back-ported from Python 3.x
                intersection = set(tags) & {x, y}
                i += intersection == {x, y}
            if i > 0:
                links.append(
                    {'source': items[x], 'target': items[y], 'value': i})
        
        collection = json.dumps({'nodes': nodes, 'links': links})
        print(collection)



# no need to run server!
# (andsnews) $ python -m unittest api/test_graph.py
