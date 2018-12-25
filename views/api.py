import datetime
import time
from operator import itemgetter

import numpy as np
from google.appengine.api import search
from google.appengine.ext import ndb
from unidecode import unidecode

from models import Counter, INDEX, PHOTO_FILTER

PERCENTILE = 80


class cached_property(object):
    """ Decorator for read-only properties evaluated only once within TTL period.
        https://wiki.python.org/moin/PythonDecoratorLibrary#Cached_Properties """
    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value


class Cached(object):
    @cached_property(ttl=5)
    def counters(self):
        tmp = {}
        for field in PHOTO_FILTER:
            query = Counter.query(Counter.forkind == 'Photo', Counter.field == field)
            tmp[field] = [counter for counter in query if counter.count > 0]

        return tmp


cached = Cached()
DATA = cached.counters


def counters_values():
    result = {}
    for field in DATA.keys():
        _list = [counter.value for counter in DATA[field]]
        if field == 'year':
            result[field] = sorted(_list, reverse=True)
        else:
            result[field] = sorted(_list)

    return result


def available_filters():
    collection = []
    for field in sorted(DATA.keys(), reverse=True):
        _list = [{
            'field_name': field,
            'count': counter.count,
            'name': counter.value,
            'serving_url': counter.repr_url,
            'repr_stamp': counter.repr_stamp
        } for counter in DATA[field]]
        if field == 'year':
            _list = sorted(_list, key=itemgetter('name'), reverse=True)
        else:
            _list = sorted(_list, key=itemgetter('name'))
        collection.extend(_list)

    current = datetime.datetime.now().year
    if collection:
        limit = np.percentile([d['count'] for d in collection], PERCENTILE)
        for item in collection:
            item['show'] = True if (item['field_name'] == 'year' and item['name'] == current) \
                else item['count'] > int(limit)

    return [x for x in collection if x['show']]


class SearchPaginator(object):
    def __init__(self, querystring, per_page):
        self.querystring = unidecode(querystring.decode('utf-8'))
        self.per_page = per_page

        self.options = {
            'limit': self.per_page,
            'ids_only': True,
            'sort_options': search.SortOptions(
                expressions=[
                    search.SortExpression(
                        expression='stamp',
                        direction=search.SortExpression.DESCENDING,
                        default_value=time.mktime(datetime.datetime(1970, 1, 1).timetuple()))
                ]
            )
        }

    def page(self, token=None):
        objects, next_token, number_found, error = [], None, 0, None
        if token is not None:
            self.options['cursor'] = search.Cursor(web_safe_string=token)
        else:
            self.options['cursor'] = search.Cursor()

        if self.querystring:
            try:
                query = search.Query(
                    query_string=self.querystring,
                    options=search.QueryOptions(**self.options)
                )
                found = INDEX.search(query)
                results = found.results
            except search.Error as e:
                error = e.message
            else:
                number_found = found.number_found
                keys = [ndb.Key(urlsafe=doc.doc_id) for doc in results]
                objects = ndb.get_multi(keys)

                if found.cursor is not None:
                    next_token = found.cursor.web_safe_string

        return objects, number_found, next_token, error
