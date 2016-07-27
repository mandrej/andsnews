import json
import logging
import webapp2
from operator import itemgetter
from google.appengine.api import memcache
from google.appengine.ext import ndb
from handlers import LazyEncoder, Paginator, SearchPaginator
from models import Cloud
from config import TIMEOUT

LIMIT = 12


class RestHandler(webapp2.RequestHandler):
    def render(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        # self.response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class Collection(RestHandler):
    def get(self, kind=None, field=None, value=None):
        page = self.request.get('page', None)
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
            fields = ['date', 'tags', 'model']
        elif kind == 'entry':
            fields = ['date', 'tags', 'author']

        data = []
        for field in fields:
            mem_key = kind.title() + '_' + field
            cloud = Cloud(mem_key).get_list()

            limit = cloud_limit(cloud)
            items = [x for x in cloud if x['count'] > limit]

            if field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
                items = sorted(items, key=itemgetter('count'), reverse=True)

            if field == 'date':
                items = sorted(items, key=itemgetter('name'), reverse=True)
            elif field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
                items = sorted(items, key=itemgetter('name'), reverse=False)
            elif field == 'color':
                items = sorted(items, key=itemgetter('order'))

            for item in items:
                query = model.query_for(field, item['name'])
                res = query.fetch(1)
                try:
                    obj = res[0]
                except IndexError:
                    pass
                else:
                    if kind == 'photo':
                        item['repr_url'] = obj.serving_url + '=s400'
                    elif kind == 'entry' and obj.front != -1:
                        item['repr_url'] = obj.image_url(obj.front) + '/normal'

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


class Download(webapp2.RequestHandler):
    def get(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        obj = key.get()
        buff = obj.buffer
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s.jpg' % key.string_id()
        self.response.write(buff)
