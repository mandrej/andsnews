from __future__ import division
from collections import defaultdict

from google.appengine.ext import ndb
from google.appengine.api import memcache
from webapp2_extras.appengine.users import admin_required
from datetime import datetime, timedelta
from colormath.color_objects import HSLColor
from models import Photo, Entry, Comment, Feed, Counter, Cloud, KEYS
from views.entry import make_thumbnail
from handlers import BaseHandler, csrf_protected, Paginator, Filter, touch_appcache
from config import filesizeformat, PER_PAGE, HUE


class Cache(BaseHandler):
    def get(self):
        data = dict(zip(KEYS, [None] * len(KEYS)))
        data.update(memcache.get_multi(KEYS))
        self.render_json(data)

    def put(self, mem_key):
        cloud = Cloud(mem_key)
        cloud.rebuild()
        self.render_json(cloud.get_cache())

    def delete(self, mem_key):
        memcache.delete(mem_key)
        self.render_json(None)


class Index(BaseHandler):
    @admin_required
    def get(self):
        stats = memcache.get_stats()
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        all = hits + misses

        delta = stats.get('oldest_item_age', 0)  # seconds
        weeks, rem1 = divmod(delta, 604800)
        days, rem2 = divmod(rem1, 86400)
        hours, rem3 = divmod(rem2, 3600)
        minutes, seconds = divmod(rem3, 60)
        oldest = datetime.now() - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

        try:
            hit_ratio = 100 * hits / all
        except ZeroDivisionError:
            hit_ratio = 0
        data = {'photo_count': Photo.query().order(-Photo.date).count(),
                'entry_count': Entry.query().order(-Entry.date).count(),
                'comment_count': Comment.query().order(-Comment.date).count(),
                'feeds_count': Feed.query().order(-Feed.date).count(),
                'stats': stats,
                'oldest': oldest,
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

    @csrf_protected
    def post(self):
        params = dict(self.request.POST)
        key = ndb.Key(urlsafe=params['safe_key'])
        if 'body' in params:
            obj = key.get()
            obj.body = params['body']
            touch_appcache()
            obj.put()
        else:
            key.delete()
        self.render_json({'success': True})


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
                'archive': Cloud('Entry_date').get_list()}
        self.render_template('admin/images.html', data)

    @csrf_protected
    def post(self):
        params = dict(self.request.POST)
        key = ndb.Key(urlsafe=params['safe_key'])
        if params['action'] == 'delete':
            obj = key.get()
            obj.small = None
            obj.put()
            data = {'success': True}
        elif params['action'] == 'make':
            buff, mime = make_thumbnail('Entry', key.string_id(), 'small')
            data = {'success': True, 'small': filesizeformat(len(buff))}
        self.render_json(data)


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
                'archive': Cloud('Photo_date').get_list()}
        self.render_template('admin/blobs.html', data)


class Feeds(BaseHandler):
    @admin_required
    def get(self):
        query = Feed.query().order(-Feed.date)
        self.render_template('admin/feeds.html', {'objects': query})

    @csrf_protected
    def post(self):
        slug = self.request.get('action:feed')
        if slug:
            touch_appcache()
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

    @csrf_protected
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


class Spectra(BaseHandler):
    def get(self):
        sat = int(self.request.get('sat', 20))
        lum = int(self.request.get('lum', 40))
        spectra = defaultdict(list)
        for row in HUE:
            for hue in row['span']:
                color = HSLColor(hue, sat / 100.0, lum / 100.0)
                hsl = 'hsl({0}, {1:.0%}, {2:.0%})'.format(*color.get_value_tuple())
                spectra[row['name']].append(hsl)

        self.render_json(spectra)