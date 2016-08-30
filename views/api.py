import os
import json
import logging
import webapp2
import datetime
from slugify import slugify
from google.appengine.api import users, search, app_identity, datastore_errors
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from models import Cloud, cloud_representation, Photo, Entry, INDEX
from config import DEVEL

LIMIT = 12 if DEVEL else 48
KEYS = ('Photo_date', 'Photo_tags', 'Photo_model')
BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())


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
        cloud = Cloud(mem_key).get()
        self.render(cloud.keys())


class Collection(RestHandler):
    def get(self, kind=None, field=None, value=None):
        page = self.request.get('page', None)

        # SPECIFIC
        if kind == 'entry' and field == 'show':
            obj = ndb.Key(urlsafe=value).get()
            if obj is None:
                self.abort(404)
            objects = [obj]
            token = None
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


class KindFilter(RestHandler):
    def get(self, kind=None):
        if kind == 'photo':
            fields = ['date', 'tags', 'model']
        elif kind == 'entry':
            fields = ['date', 'tags']

        data = cloud_representation(kind, fields)
        self.render(data)


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


class Cache(RestHandler):
    def put(self, mem_key):
        cloud = Cloud(mem_key)
        cloud.rebuild()
        self.render(cloud.get_cache())


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
        else:
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
        data['tags'] = tags
        # fix empty values
        values = map(lambda x: x if x != '' else None, data.values())
        data = dict(zip(data.keys(), values))
        # fix date
        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S')

        if kind == 'photo':
            if data['focal_length']:
                data['focal_length'] = float(data['focal_length'])
            if data['aperture']:
                data['aperture'] = float(data['aperture'])
            if data['iso']:
                data['iso'] = int(data['iso'])

        # elif kind == 'entry':
        #     logging.error(data)

        obj.edit(data)

    def delete(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        key.delete()


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
