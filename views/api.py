import datetime
import json
import time
from urlparse import urlparse

import webapp2
from google.appengine.api import users, search, datastore_errors
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb, deferred
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from config import DEVEL, START_MSG
from mapper import push_message, Indexer, Builder, Unbound, RemoveFields
from models import Counter, Photo, INDEX, PHOTO_FILTER
from slugify import slugify

LIMIT = 25
PERCENTILE = 50 if DEVEL else 80
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

        return [x for x in objects if x is not None], number_found, next_token, error


class RestHandler(webapp2.RequestHandler):
    def render(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        # self.response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class WarmUp(RestHandler):
    def get(self):
        self.render({'warmup': True})


class Suggest(RestHandler):
    def get(self, mem_key):
        kind, field = mem_key.split('_')
        query = Counter.query(Counter.forkind == kind, Counter.field == field)
        self.render([counter.value for counter in query])


class Collection(RestHandler):
    def get(self, kind=None, field=None, value=None):
        page = self.request.get('_page', None)
        token = None

        if field == 'year':
            value = int(value)
        query = Photo.query_for(field, value)
        paginator = Paginator(query, per_page=LIMIT)
        objects, token = paginator.page(page)  # [], None

        self.render({
            'objects': objects,
            'filter': {'field': field, 'value': value} if (field and value) else None,
            '_page': page,
            '_next': token
        })


class PhotoRecent(RestHandler):
    def get(self):
        page = self.request.get('_page', None)
        token = None

        query = Photo.query().order(-Photo.date)
        paginator = Paginator(query, per_page=LIMIT)
        objects, token = paginator.page(page)  # [], None

        self.render({
            'objects': objects,
            '_page': page,
            '_next': token
        })


class Find(RestHandler):
    def get(self, find):
        page = self.request.get('_page', None)
        paginator = SearchPaginator(find, per_page=LIMIT)
        objects, number_found, token, error = paginator.page(page)

        self.render({
            'objects': objects,
            'phrase': find.strip(),
            'number_found': number_found,
            '_page': page,
            '_next': token,
            'error': error
        })


class BackgroundIndex(RestHandler):
    def post(self, kind):
        token = self.request.json.get('token', None)
        if token is not None:
            runner = Indexer()

            if kind == 'photo':
                runner.KIND = Photo

            runner.TOKEN = token
            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, batch_size=10, _queue='background')


class BackgroundUnbound(RestHandler):
    def post(self, kind):
        token = self.request.json.get('token', None)
        if kind == 'photo' and token is not None:
            runner = Unbound()
            runner.TOKEN = token

            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, batch_size=10, _queue='background')


class BackgroundFix(RestHandler):
    def post(self, kind):
        token = self.request.json.get('token', None)
        # if kind == 'photo' and token is not None:
        if kind == 'counter' and token is not None:
            # runner = Fixer()
            runner = RemoveFields()
            # runner.KIND = Photo
            runner.KIND = Counter
            # runner.DATE_START = datetime.datetime.strptime('2013-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')
            # runner.DATE_END = datetime.datetime.strptime('2013-12-31T23:59:59', '%Y-%m-%dT%H:%M:%S')
            runner.TOKEN = token

            push_message(runner.TOKEN, START_MSG)
            deferred.defer(runner.run, batch_size=10, _queue='background')


class BackgroundBuild(RestHandler):
    def post(self, mem_key):
        kind, field = mem_key.split('_', 1)
        token = self.request.json.get('token', None)
        if token is not None:
            runner = Builder()
            if kind == 'Photo':  # Title case!
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

    def post(self, kind=None):
        data = dict(self.request.params)  # {'file': FieldStorage('file', u'SDIM4151.jpg')}
        if kind == 'photo':
            fs = data['file']
            obj = Photo(headline=fs.filename)
            res = obj.add(fs)

        self.render(res)

    def put(self, kind=None, safe_key=None):
        key = get_key(safe_key)
        if key is None:
            self.abort(404)
        obj = key.get()

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
        dt = data['date'].strip().split('.')[0]  # no millis
        data['date'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')

        if kind == 'photo':
            if data['focal_length']:
                data['focal_length'] = round(float(data['focal_length']), 1)
            if data['aperture']:
                data['aperture'] = float(data['aperture'])
            if data['iso']:
                data['iso'] = int(data['iso'])

        obj.edit(data)

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


class SiteMap(webapp2.RequestHandler):
    def get(self):
        uri = urlparse(self.uri_for('sitemap', _full=True))
        collection = Photo.query().order(-Photo.date).fetch(100)
        out = ''
        for obj in collection:
            link = '{}://{}/#/item/{}'.format(uri.scheme, uri.netloc, obj.key.urlsafe())
            out += TEMPLATE_ROW.format(**{
                'loc': link,
                'lastmod': obj.date.strftime('%Y-%m-%d')
            })
        self.response.headers = {
            'Content-Type': 'application/xml'
        }
        self.response.write(TEMPLATE_WRAPPER.format(out))


class Info(RestHandler):
    def get(self):
        data = {
            'photo': {'count': Photo.query().count()},
        }
        data['photo']['counters'] = ['Photo_%s' % x for x in PHOTO_FILTER]
        self.render(data)
