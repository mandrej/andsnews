import json
import logging
import webapp2
from operator import itemgetter
from google.appengine.ext import ndb
from handlers import LazyEncoder, Paginator, SearchPaginator, cloud_limit
from models import Cloud

LIMIT = 12


class RestHandler(webapp2.RequestHandler):
    def render(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        self.response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
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


class KindFilter(RestHandler):  # from handlers.RenderCloud
    def get(self, kind=None):
        fields = ['date', 'tags', 'author']
        model = ndb.Model._kind_map.get(kind.title())
        data = []

        for field in fields:
            mem_key = kind.title() + '_' + field
            items = Cloud(mem_key).get_list()

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

            limit = cloud_limit(items)
            data.append({
                'field_name': field,
                'items': items,
                'limit': limit
            })

        self.render(data)


class Find(RestHandler):
    def get(self):
        find = self.request.get('find').strip()
        page = self.request.get('page', None)
        paginator = SearchPaginator(find, per_page=LIMIT)
        objects, number_found, token, error = paginator.page(page)

        self.render({
            'objects': objects,
            'phrase': find,
            'number_found': number_found,
            'page': page,
            'next': token,
            'error': error
        })
