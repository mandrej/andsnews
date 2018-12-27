from __future__ import division

import datetime
import time
from operator import itemgetter

from flask.json import JSONEncoder
from google.appengine.api import users, search
from google.appengine.ext import ndb
from unidecode import unidecode

from config import PERCENTILE
from models import Counter, INDEX


class CustomJSONEncoder(JSONEncoder):
    """ json mapper helper """
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, users.User):
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


class SearchPaginator(object):
    def __init__(self, querystring, per_page):
        self.querystring = unidecode(unicode(querystring))
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
