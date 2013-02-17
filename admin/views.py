from __future__ import division
import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import memcache
from webapp2_extras.appengine.users import admin_required
from models import Photo, Entry, Comment, Feed, Counter, KEYS
from entry.views import make_thumbnail
from common import BaseHandler, Paginator, Filter, count_property, count_colors, make_cloud, filesizeformat
from settings import PER_PAGE


class Cache(webapp2.RequestHandler):
    def get(self):
        data = dict(zip(KEYS, [None]*len(KEYS)))
        data.update(memcache.get_multi(KEYS))
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(data))

    def put(self, key):
        kind, field = key.split('_')
        if field == 'colors':
            content = count_colors()
        else:
            content = count_property(kind, field)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(content))

    def delete(self, key):
        memcache.delete(key)
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(None))


class Index(BaseHandler):
    @admin_required
    def get(self):
        stats = memcache.get_stats()
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        all = hits + misses
        try:
            hit_ratio = 100 * hits / all
        except ZeroDivisionError:
            hit_ratio = 0
        data = {'photo_count': Photo.query().order(-Photo.date).count(),
                'entry_count': Entry.query().order(-Entry.date).count(),
                'comment_count': Comment.query().order(-Comment.date).count(),
                'feeds_count': Feed.query().order(-Feed.date).count(),
                'stats': stats,
                'hit_ratio': hit_ratio}
        self.render_template('admin/index.html', data)


class Comments(BaseHandler):
    @admin_required
    def get(self):
        query = Comment.query().order(-Comment.date)
        page = int(self.request.get('page', 1))
        paginator = Paginator(query, 10)
        objects, has_next = paginator.page(page)
        data = {'objects': objects, 'page': page, 'has_next': has_next, 'has_previous': page > 1}
        self.render_template('admin/comments.html', data)

    def post(self):
        params = dict(self.request.POST)
        key = ndb.Key(urlsafe=params['safekey'])
        if 'body' in params:
            obj = key.get()
            obj.body = params['body']
            obj.put()
        else:
            key.delete()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'success': True}))
        return self.response


#def thumbnail_color(request):
#    params = request.POST
#    parentkind = params['kind']
#    slug = params['slug']
#
#    obj = ndb.Key(parentkind, slug, 'Picture', slug).get()
#    obj.rgb = median(obj.small)
#    obj.put()
#    photo = ndb.Key(parentkind, slug).get()
#    photo.hue, photo.lum, photo.sat = range_names(*obj.hls)
#    photo.put()
#    response = webapp2.Response(content_type='application/json')
#    response.write(json.dumps({'success': True, 'hex': obj.hex}))
#    return response

#model = ndb.Model._kind_map.get(kind)


class Images(BaseHandler):
    @admin_required
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Entry._properties[k] == v for k, v in f.parameters.items()]
        query = Entry.query(*filters).order(-Entry.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query, per_page=6)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1,
                'archive': make_cloud('Entry', 'date')}
        self.render_template('admin/images.html', data)

    def post(self):
        params = dict(self.request.POST)
        key = ndb.Key(urlsafe=params['safekey'])
        if params['action'] == 'delete':
            obj = key.get()
            obj.small = None
            obj.put()
            data = {'success': True}
        elif params['action'] == 'make':
            buff, mime = make_thumbnail('Entry', key.string_id(), 'small')
            data = {'success': True, 'small': filesizeformat(len(buff))}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(data))
        return self.response


class Blobs(BaseHandler):
    @admin_required
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1,
                'archive': make_cloud('Photo', 'date')}
        self.render_template('admin/blobs.html', data)


class Feeds(BaseHandler):
    @admin_required
    def get(self):
        query = Feed.query().order(-Feed.date)
        self.render_template('admin/feeds.html', {'objects': query})

    def post(self):
        slug = self.request.get('action:feed')
        if slug:
            memcache.delete(slug)
        self.redirect('/admin/feeds')


class Counters(BaseHandler):
    @admin_required
    def get(self, per_page=PER_PAGE):
        query = Counter.query().order(Counter.field)
        page = int(self.request.get('page', 1))
        paginator = Paginator(query, per_page=per_page)
        objects, has_next = paginator.page(page)
        data = {'objects': objects, 'page': page, 'has_next': has_next, 'has_previous': page > 1}
        self.render_template('admin/counters.html', data)

    def post(self):
        cntx = ndb.get_context()
        cntx.set_cache_policy(False)
        if self.request.get('action:delete'):
            key = ndb.Key(urlsafe=self.request.get('action:delete'))
            key.delete()
        elif self.request.get('action:edit'):
            input_id = self.request.get('action:edit')
            key = ndb.Key(urlsafe=input_id)
            obj = key.get()
            obj.count = int(self.request.get('count.%s' % input_id))
            obj.put()

        self.redirect('/admin/counters')