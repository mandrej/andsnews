import json
import logging
import webapp2
import datetime
import numpy as np
from slugify import slugify
from operator import itemgetter
from google.appengine.api import users, search, datastore_errors
from google.appengine.ext import ndb, deferred
from google.appengine.datastore.datastore_query import Cursor
from models import Counter, Photo, Entry, INDEX, PHOTO_FILTER
from mapper import Indexer, Unbound, Builder, Fixer
from config import DEVEL

LIMIT = 12
PERCENTILE = 50 if DEVEL else 80


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, users.User):
            return obj.email()
        return obj


class Paginator(object):
    def __init__(self, query, per_page):
        self.query = query
        self.per_page = per_page

    def page(self, token=None):
        try:
            cursor = Cursor(urlsafe=token)
        except datastore_errors.BadValueError:
            webapp2.abort(404)

        objects, cursor, has_next = self.query.fetch_page(self.per_page, start_cursor=cursor)
        next_token = cursor.urlsafe() if has_next else None
        return [x for x in objects if x is not None], next_token


class SearchPaginator(object):
    def __init__(self, querystring, per_page):
        self.querystring = querystring
        self.per_page = per_page

        self.options = {
            'limit': self.per_page,
            'ids_only': True,
            'sort_options': search.SortOptions(
                expressions=[
                    search.SortExpression(
                        expression='year * 12 + month',
                        direction=search.SortExpression.DESCENDING, default_value=2030*12)
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

        return [x for x in objects if x is not None], number_found, next_token, error


class RestHandler(webapp2.RequestHandler):
    def render(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        # self.response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class Suggest(RestHandler):
    def get(self, mem_key):
        kind, field = mem_key.split('_')
        query = Counter.query(Counter.forkind == kind, Counter.field == field)
        self.render([counter.value for counter in query])


class Collection(RestHandler):
    def get(self, kind=None, field=None, value=None):
        page = self.request.get('page', None)
        token = None

        # SPECIFIC
        if kind == 'entry' and field == 'show':
            obj = ndb.Key(urlsafe=value).get()
            if obj is None:
                self.abort(404)
            objects = [obj]
        else:
            model = ndb.Model._kind_map.get(kind.title())
            query = model.query_for(field, value)
            paginator = Paginator(query, per_page=LIMIT)
            objects, token = paginator.page(page)  # [], None

        self.render({
            'objects': objects,
            'filter': {'field': field, 'value': value} if (field and value) else None,
            'page': page,
            'next': token
        })


class PhotoFilters(RestHandler):
    def get(self):
        collection = []
        for field, _ in sorted(PHOTO_FILTER.items(), key=itemgetter(1)):
            query = Counter.query(Counter.forkind == 'Photo', Counter.field == field)
            items = []
            for counter in query:
                items.append({
                    'field_name': field,
                    'count': counter.count,
                    'name': counter.value,
                    'repr_url': counter.repr_url})

            if field == 'date':
                items = sorted(items, key=itemgetter('name'), reverse=True)
            collection.extend(items)

        limit = np.percentile([d['count'] for d in collection], PERCENTILE)
        for item in collection:
            item['show'] = item['count'] > int(limit)

        self.render(collection)


class Find(RestHandler):
    def get(self, find):
        page = self.request.get('page', None)
        paginator = SearchPaginator(find, per_page=LIMIT)
        objects, number_found, token, error = paginator.page(page)

        self.render({
            'objects': objects,
            'phrase': find.strip(),
            'number_found': number_found,
            'page': page,
            'next': token,
            'error': error
        })


class BackgroundIndex(RestHandler):
    def post(self, kind):
        user_id = self.request.json.get('userId', None)
        if user_id is not None:
            if kind == 'photo':
                runner = Indexer()
                runner.KIND = Photo

            elif kind == 'entry':
                runner = Indexer()
                runner.KIND = Entry

            runner.CHANNEL_NAME = '%s_index.json' % kind

            deferred.defer(runner.run, batch_size=10, _queue='background')
            self.render({'channelId': runner.CHANNEL_NAME, 'userId': user_id})


class BackgroundUnbound(RestHandler):
    def post(self, kind):
        user_id = self.request.json.get('userId', None)
        if kind == 'photo' and user_id is not None:
            runner = Unbound()
            runner.KIND = Photo
            runner.CHANNEL_NAME = '%s_unbound.json' % kind

            deferred.defer(runner.run, batch_size=10, _queue='background')
            self.render({'channelId': runner.CHANNEL_NAME, 'userId': user_id})


class BackgroundFix(RestHandler):
    def post(self, kind):
        user_id = self.request.json.get('userId', None)
        if kind == 'photo' and user_id is not None:
            runner = Fixer()
            runner.KIND = Photo
            runner.DATE_START = datetime.datetime.strptime('2013-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')
            runner.DATE_END = datetime.datetime.strptime('2013-12-31T23:59:59', '%Y-%m-%dT%H:%M:%S')
            runner.CHANNEL_NAME = '%s_fix.json' % kind

            deferred.defer(runner.run, batch_size=10, _queue='background')
            self.render({'channelId': runner.CHANNEL_NAME, 'userId': user_id})


class BackgroundBuild(RestHandler):
    def post(self, mem_key):
        kind, field = mem_key.split('_', 1)
        token = self.request.json.get('token', None)

        if token is not None:
            runner = Builder()
            if kind == 'Photo':  # Title case!
                runner.KIND = Photo
            elif kind == 'Entry':
                runner.KIND = Entry

            runner.VALUES = []
            runner.FIELD = field
            runner.TOKEN = token
            # runner.CHANNEL_NAME = '%s.json' % mem_key

            deferred.defer(runner.run, batch_size=10, _queue='background')
            # self.render({'token': token})


class Crud(RestHandler):
    def get(self, kind=None, safe_key=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        self.render(obj)

    def post(self, kind=None):
        data = dict(self.request.params)  # {'file': FieldStorage('file', u'SDIM4151.jpg')}
        if kind == 'photo':
            fs = data['file']
            obj = Photo(headline=fs.filename)
            res = obj.add(fs)
        elif kind == 'entry':
            obj = Entry(headline=data['headline'])
            # fix tags
            if 'tags' in data:
                if data['tags'].strip() != '':
                    tags = map(unicode.strip, data['tags'].split(','))
                else:
                    tags = []
            else:
                tags = []
            data['tags'] = tags
            # fix author
            if 'author' in data:
                email = data['author']
                data['author'] = users.User(email=email)

            # fix empty values
            values = map(lambda x: x if x != '' else None, data.values())
            data = dict(zip(data.keys(), values))
            res = obj.add(data)

        self.render(res)

    def put(self, kind=None, safe_key=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)

        data = dict(self.request.params)
        # fix tags
        if 'tags' in data:
            if data['tags'].strip() != '':
                tags = map(unicode.strip, data['tags'].split(','))
            else:
                tags = []
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
        dt = data['date'].strip().split('.')[0]  # no milis
        data['date'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')

        if kind == 'photo':
            if data['focal_length']:
                data['focal_length'] = round(float(data['focal_length']), 1)
            if data['aperture']:
                data['aperture'] = float(data['aperture'])
            if data['iso']:
                data['iso'] = int(data['iso'])

        # elif kind == 'entry':
        #     logging.error(data)

        obj.edit(data)

    def delete(self, safe_key):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)

        obj.remove()


class Download(webapp2.RequestHandler):
    def get(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        obj = key.get()
        buff = obj.buffer
        self.response.headers = {
            'Content-Type': 'image/jpeg',
            'Content-Disposition': 'attachment; filename=%s.jpg' % str(slugify(obj.headline))
        }
        self.response.write(buff)


class Info(RestHandler):
    def get(self):
        fields = [x[0] for x in sorted(PHOTO_FILTER.items(), key=itemgetter(1))]
        data = {
            'photo': {
                'count': Photo.query().count(),
                'counters': ['Photo_%s' % x for x in fields]
            }
        }
        self.render(data)
