import json
import webapp2
from operator import itemgetter
from google.appengine.ext import ndb
from handlers import LazyEncoder, Paginator, cloud_limit
from models import Cloud
from config import PHOTOS_PER_PAGE, ENTRIES_PER_PAGE


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
        per_page = PHOTOS_PER_PAGE if kind == 'photo' else ENTRIES_PER_PAGE
        paginator = Paginator(query, per_page)
        objects, token = paginator.page(page)

        if not objects:
            self.abort(404)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'next': token}

        self.render(data)


class KindFilter(RestHandler):
    def get(self, kind=None):
        fields = ['tags', 'date', 'author']
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

            limit = cloud_limit(items)
            data.append({
                'field_name': field,
                'items': items,
                'limit': limit
            })

        self.render(data)
