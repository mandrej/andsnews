import os
import json
import logging
import webapp2
import datetime
from operator import itemgetter
from slugify import slugify
from google.appengine.api import users, memcache, app_identity
from google.appengine.ext import ndb, blobstore, deferred
from handlers import LazyEncoder, Paginator, SearchPaginator
from models import Cloud, Entry, Photo
from config import TIMEOUT

LIMIT = 12
KEYS = ('Photo_date', 'Photo_tags', 'Photo_model')
        # 'Entry_date', 'Entry_tags', 'Entry_author')
BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())


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
            objects, token = paginator.page(page)
            if not objects:
                self.abort(404)

        self.render({
            'objects': objects,
            'filter': {'field': field, 'value': value} if (field and value) else None,
            'page': page,
            'next': token
        })


def cloud_limit(items):
    """
    Returns limit for the specific count. Show only if count > limit
    :param items: dict {Photo_tags: 10, _date: 119, _eqv: 140, _iso: 94, _author: 66, _lens: 23, _model: 18, _color: 73
    :return: int
    """
    _curr = 0
    _sum5 = sum((x['count'] for x in items)) * 0.05
    if _sum5 < 1:
        return 0
    else:
        _on_count = sorted(items, key=itemgetter('count'))
        for item in _on_count:
            _curr += item['count']
            if _curr >= _sum5:
                return item['count']


def cloud_representation(kind):
    model = ndb.Model._kind_map.get(kind.title())
    data = memcache.get('%s_representation' % kind)

    if data is None:
        if kind == 'photo':
            fields = ('date', 'tags', 'model')
        elif kind == 'entry':
            fields = ('date', 'tags')

        data = []
        for field in fields:
            mem_key = kind.title() + '_' + field
            cloud = Cloud(mem_key).get_list()

            limit = cloud_limit(cloud)
            items = [x for x in cloud if x['count'] > limit]

            if field == 'date':
                items = sorted(items, key=itemgetter('name'), reverse=True)
            elif field in ('tags', 'author', 'model', 'lens', 'iso'):
                items = sorted(items, key=itemgetter('name'), reverse=False)
            elif field == 'color':
                items = sorted(items, key=itemgetter('order'))

            for item in items:
                obj = model.latest_for(field, item['name'])
                if obj is not None:
                    if kind == 'photo':
                        item['repr_url'] = obj.serving_url + '=s400'
                    elif kind == 'entry':
                        item['repr_url'] = obj.front_img

            data.append({
                'field_name': field,
                'items': items
            })
        memcache.set('%s_representation' % kind, data, TIMEOUT * 2)

    return data


class KindFilter(RestHandler):  # from handlers.RenderCloud
    def get(self, kind=None):
        data = cloud_representation(kind)
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
        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%d')

        if kind == 'photo':
            if data['focal_length']:
                data['focal_length'] = float(data['focal_length'])
            if data['aperture']:
                data['aperture'] = float(data['aperture'])
            if data['iso']:
                data['iso'] = int(data['iso'])

        elif kind == 'entry':
            logging.error(data)

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
        # self.response.headers['Content-Disposition'] = 'attachment; filename=download.jpg'
        # self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.write(buff)
