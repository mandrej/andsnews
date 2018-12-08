import datetime
import json
import time
import pytz
import logging
from operator import itemgetter

import numpy as np
import webapp2
from google.appengine.api import users, search
from google.appengine.ext import ndb, deferred
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from unidecode import unidecode
from urlparse import urlparse

from config import START_MSG
from mapper import push_message, Missing, Indexer, Builder, Unbound
from models import Counter, Photo, INDEX, PHOTO_FILTER, slugify

LIMIT = 24
PERCENTILE = 80
TZ = pytz.timezone('Europe/Belgrade')

TEMPLATE_WRAPPER = """<?xml version="1.0" encoding="UTF-8"?><urlset
xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{}</urlset>"""
TEMPLATE_ROW = """<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq>
<priority>0.3</priority></url>"""


def get_key(url_safe_str):
    # https://github.com/googlecloudplatform/datastore-ndb-python/issues/143
    key = None
    try:
        key = ndb.Key(urlsafe=url_safe_str)
    except ProtocolBufferDecodeError:
        pass
    return key


class LazyEncoder(json.JSONEncoder):
    """ json mapper helper """
    def default(self, obj):
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            """
            2018-08-16 10:39:09 -> 2018-08-16 10:39:09+02:00
            2018-01-14 13:03:01 -> 2018-01-14 13:03:01+01:00
            """
            return TZ.localize(obj).isoformat()
        elif isinstance(obj, users.User):
            return obj.email()
        return obj


class RestHandler(webapp2.RequestHandler):
    def render(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        # self.response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        self.response.write(json.dumps(data, cls=LazyEncoder))


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


class Find(RestHandler):
    def get(self, find):
        page = self.request.get('_page', None)
        per_page = int(self.request.get('per_page', LIMIT))
        paginator = SearchPaginator(find, per_page=per_page)
        objects, number_found, token, error = paginator.page(page)

        self.render({
            'objects': objects,
            'filter': {'field': 'search', 'value': find.strip()},
            # 'number_found': number_found,
            '_page': page if page else 'FP',
            '_next': token,
            'error': error
        })


class Suggest(RestHandler):
    def get(self, mem_key):
        kind, field = mem_key.split('_')
        query = Counter.query(Counter.forkind == kind, Counter.field == field)
        self.render([counter.value for counter in query if counter.count > 0])


def available_filters():
    collection = []
    for field in PHOTO_FILTER:
        query = Counter.query(Counter.forkind == 'Photo', Counter.field == field)
        items = []
        for counter in query:
            items.append({
                'field_name': field,
                'count': counter.count,
                'name': counter.value,
                'serving_url': counter.repr_url,
                'repr_stamp': counter.repr_stamp})

        if field == 'year':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        collection.extend(items)

    current = datetime.datetime.now().year
    if collection:
        limit = np.percentile([d['count'] for d in collection], PERCENTILE)
        for item in collection:
            item['show'] = True if (item['field_name'] == 'year' and item['name'] == current) \
                else item['count'] > int(limit)

    return [x for x in collection if x['show']]


class PhotoFilters(RestHandler):
    def get(self):
        self.render({
            'count': Photo.query().count(),
            'filters': available_filters()
        })


class Notify(RestHandler):
    def post(self):
        token = self.request.json.get('token', None)
        text = self.request.json.get('text', None)
        push_message(token, text)


class BackgroundIndex(RestHandler):
    def post(self):
        token = self.request.json.get('token', None)
        if token is not None:
            runner = Indexer()
            runner.KIND = Photo
            runner.TOKEN = token
            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, batch_size=10, _queue='background')


class BackgroundUnbound(RestHandler):
    def post(self):
        token = self.request.json.get('token', None)
        if token is not None:
            runner = Unbound()
            runner.TOKEN = token
            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, _queue='background')


class BackgroundDeleted(RestHandler):
    def post(self):
        token = self.request.json.get('token', None)
        if token is not None:
            runner = Missing()
            runner.KIND = Photo
            runner.TOKEN = token
            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, batch_size=10, _queue='background')


class BackgroundBuild(RestHandler):
    def post(self, mem_key):
        kind, field = mem_key.split('_', 1)
        token = json.loads(self.request.body).get('token', None)

        if kind == 'Photo' and token is not None:  # TODO Title case!
            runner = Builder()
            runner.KIND = Photo
            runner.VALUES = []
            runner.FIELD = field
            runner.TOKEN = token
            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, batch_size=10, _queue='background')


class Crud(RestHandler):
    def get(self, safe_key=None):
        key = get_key(safe_key)
        if key is None:
            self.abort(404)
        self.render(key.get())

    def post(self):
        resList = []
        # {'photos', FieldStorage('photos', u'light-rain.jpg')}
        for fs in self.request.POST.getall('photos'):
            obj = Photo(headline=fs.filename)
            res = obj.add(fs)
            resList.append(res)
        self.render(resList)

    def put(self, safe_key=None):
        key = get_key(safe_key)
        if key is None:
            self.abort(404)
        obj = key.get()

        data = json.loads(self.request.body)  # TODO vue2
        # fix tags
        if 'tags' in data:
            tags = data['tags']
        else:
            tags = []

        data['tags'] = sorted(tags)
        # fix author
        if 'author' in data:
            email = data['author']
            data['author'] = users.User(email=email)

        # fix empty values
        values = map(lambda x: x if x != '' else None, data.values())
        data = dict(zip(data.keys(), values))
        # fix date
        dt = data['date'].strip().split('.')[0]  # no millis
        data['date'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')

        if data['focal_length']:
            data['focal_length'] = round(float(data['focal_length']), 1)
        if data['aperture']:
            data['aperture'] = float(data['aperture'])
        if data['iso']:
            data['iso'] = int(data['iso'])
        res = obj.edit(data)
        self.render(res)

    def delete(self, safe_key):
        key = get_key(safe_key)
        if key is None:
            self.abort(404)
        key.get().remove()


class Download(webapp2.RequestHandler):
    def get(self, safe_key):
        key = get_key(safe_key)
        if key is None:
            self.abort(404)
        obj = key.get()
        self.response.headers = {
            'Content-Type': 'image/jpeg',
            'Content-Disposition': 'attachment; filename=%s.jpg' % str(slugify(obj.headline))
        }
        self.response.write(obj.buffer)


# class SiteMap(webapp2.RequestHandler):
#     def get(self):
#         uri = urlparse(self.uri_for('sitemap', _full=True))
#         collection = Photo.query().order(-Photo.date).fetch(100)
#         out = ''
#         for obj in collection:
#             link = '{}://{}/item/{}'.format(uri.scheme, uri.netloc, obj.key.urlsafe())
#             out += TEMPLATE_ROW.format(**{
#                 'loc': link,
#                 'lastmod': TZ.localize(obj.date).isoformat()
#             })
#         self.response.headers = {
#             'Content-Type': 'application/xml'
#         }
#         self.response.write(TEMPLATE_WRAPPER.format(out))


class Info(RestHandler):
    def get(self):
        data = ['Photo_%s' % x for x in PHOTO_FILTER]
        self.render(data)
