from __future__ import division

import datetime
import time
from operator import itemgetter

from flask.json import JSONEncoder
from google.appengine.api import users, datastore_errors
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from unidecode import unidecode

from config import PERCENTILE
from models import Counter


class CustomJSONEncoder(JSONEncoder):
    """ json mapper helper """
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, users.User):
            # TODO remove users api
            return obj.email()
        return JSONEncoder.default(self, obj)


def counters_values():
    data = Counter.all_photo_filter()
    result = {}
    for field in data.keys():
        _list = [counter.value for counter in data[field]]
        if field == 'year':
            result[field] = sorted(_list, reverse=True)
        else:
            result[field] = sorted(_list)
    return result


def available_filters():
    data = Counter.all_photo_filter()
    collection = []
    for field in sorted(data.keys(), reverse=True):
        _list = [{
            'field_name': field,
            'count': counter.count,
            'name': counter.value,
            'serving_url': counter.repr_url,
            'repr_stamp': counter.repr_stamp
        } for counter in data[field]]
        if field == 'year':
            _list = sorted(_list, key=itemgetter('name'), reverse=True)
        else:
            _list = sorted(_list, key=itemgetter('name'))
        collection.extend(_list)

    current = datetime.datetime.now().year
    if collection:
        dataset = sorted([d['count'] for d in collection])
        index = int(PERCENTILE * (len(dataset) + 1) / 100)
        limit = dataset[index]
        for item in collection:
            item['show'] = True if (item['field_name'] == 'year' and item['name'] == current) \
                else item['count'] > limit

    return [x for x in collection if x['show']]


class Paginator(object):
    def __init__(self, query, per_page):
        self.query = query
        self.per_page = per_page

    def page(self, token=None):
        error = None
        try:
            cursor = Cursor(urlsafe=token)
        except datastore_errors.BadValueError:
            error = 'Bad token'

        objects, cursor, has_next = self.query.fetch_page(self.per_page, start_cursor=cursor)
        next_token = cursor.urlsafe() if has_next else None
        return objects, next_token, error
