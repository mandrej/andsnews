from __future__ import division

import datetime
import time

from operator import itemgetter
from flask.json import JSONEncoder
from google.appengine.api import datastore_errors
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from unidecode import unidecode

from models import Photo, Counter


class CustomJSONEncoder(JSONEncoder):
    """ json mapper helper """

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
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


def counters_counts():
    """ only for Admin in console """
    data = Counter.all_photo_filter()
    result = {}
    for field in data.keys():
        _list = [{'value': counter.value, 'count': counter.count}
                 for counter in data[field]]
        if field == 'year':
            result[field] = sorted(
                _list, key=itemgetter('value'), reverse=True)
        else:
            result[field] = sorted(_list, key=itemgetter('value'))
    return result


def last_entry():
    year_counters = [counter for counter in Counter.query(
        Counter.forkind == 'Photo', Counter.field == 'year').order(-Counter.value)]
    last_year = year_counters[0]
    return last_year.serialize()


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

        objects, cursor, has_next = self.query.fetch_page(
            self.per_page, start_cursor=cursor)
        next_token = cursor.urlsafe() if has_next else None
        return objects, next_token, error
