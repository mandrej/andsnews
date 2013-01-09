from __future__ import division
import os, json, webapp2, jinja2
from google.appengine.ext import ndb, deferred
from google.appengine.api import memcache
from models import Photo, Entry, Comment, Feed, Counter, KEYS, median, range_names
from common import ENV, BaseHandler, Paginator, Filter, count_property, count_colors, make_cloud, make_thumbnail
from settings import PER_PAGE

def memcache_delete(request, key):
    memcache.delete(key)
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps(None))
    return response

def build(request, key):
    kind, field = key.split('_')
    content = count_property(kind, field)
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps(content))
    return response

def create(request, key):
    kind, field = key.split('_')
    if field == 'colors':
        content = count_colors()
    else:
        content = make_cloud(kind, field)
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps(content))
    return response

def memcahe_content(request):
    data = {}
    for key in KEYS:
        data[key] = memcache.get(key)
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps(data))
    return response

class Index(BaseHandler):
    def get(self):
        stats = memcache.get_stats()
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        all = hits + misses
        try:
            hit_ratio = 100*hits/all
        except ZeroDivisionError:
            hit_ratio = 0
        data = {
            'photo_count': Photo.query().order(-Photo.date).count(),
            'entry_count': Entry.query().order(-Entry.date).count(),
            'comment_count': Comment.query().order(-Comment.date).count(),
            'feeds_count': Feed.query().order(-Feed.date).count(),
            'stats': stats,
            'hit_ratio': hit_ratio
        }

        self.render_template('admin/index.html', data)

class Comments(BaseHandler):
#    @admin_required
    def get(self):
        query = Comment.query().order(-Comment.date)
        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query, 10)
        objects, has_next = paginator.page(page)
        data = {'objects': objects, 'page': page, 'has_next': has_next, 'has_previous': page > 1}
        self.render_template('admin/comments.html', data)


def delete_small(parentkind, oldkey):
    """ deferred.defer(delete_small, *args) """
    key = ndb.Key.from_old_key(oldkey)
    obj = key.get()
    if parentkind == 'Photo': obj.small = None
    elif parentkind == 'Entry': obj.small = None
    obj.put()

def comment_save(request):
    key = ndb.Key(urlsafe=request.POST['key'])
    obj = key.get()
    obj.body = request.POST['body']
    obj.put()
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps({'success': True}))
    return response

def comment_delete(request):
    key = ndb.Key(urlsafe=request.POST['key'])
    key.delete()
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps({'success': True}))
    return response

def thumbnail_delete(request):
    params = request.POST
    args = [params['kind'], params['key']]
    deferred.defer(delete_small, *args)
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps({'success': True}))
    return response

def thumbnail_make(request):
    params = request.POST
    parentkind = params['kind']
    slug = params['slug']
    no = small = '---'
    deferred.defer(make_thumbnail, parentkind, slug, 'small')
    if small != no: small = 3000 # filesizeformat(len(small)) # TODO
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps({'success': True, 'small': small}))
    return response

def thumbnail_color(request):
    params = request.POST
    parentkind = params['kind']
    slug = params['slug']

    obj = ndb.Key(parentkind, slug, 'Picture', slug).get()
    obj.rgb = median(obj.small)
    obj.put()
    photo = ndb.Key(parentkind, slug).get()
    photo.hue, photo.lum, photo.sat = range_names(*obj.hls)
    photo.put()
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps({'success': True, 'hex': obj.hex}))
    return response

class Thumbnails(BaseHandler):
#    @admin_required
    def get(self, kind, field=None, value=None, per_page=PER_PAGE):
        kind =kind.capitalize()
        f = Filter(field, value)
        model = ndb.Model._kind_map.get(kind)
        filters = [model._properties[k] == v for k, v in f.parameters.items()]
        query = model.query(*filters).order(-model.date)

        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query, per_page=per_page)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': f.parameters,
                'kind': kind,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        data['archive'] = make_cloud(kind, 'date')
        data['link'] = '/admin/%s/thumbnails/date' % kind.lower()
        self.render_template('admin/thumbnails.html', data)


#@admin_required
def info(request, oldkey):
    key = ndb.Key.from_old_key(oldkey)
    template = ENV.get_template('admin/info.html')
    response = webapp2.Response(content_type='text/html')
    response.out.write(template.render({'object': key.get()}))
    return response

class Feeds(BaseHandler):
    #@admin_required
    def get(self):
        query = Feed.query().order(-Feed.date)
        self.render_template('admin/feeds.html', {'objects': query})

    def post(self):
        query = Feed.query().order(-Feed.date)
        feed_slug = self.request.POST.get('action:feed')
        if feed_slug:
            if feed_slug == 'all':
                k = [x.key().name() for x in query]
                memcache.delete_multi(k)
            else:
                memcache.delete(feed_slug)
        self.redirect('/admin/feeds')

class Counters(BaseHandler):
    #@admin_required
    def get(self, per_page=PER_PAGE):
        query = Counter.query().order(Counter.field)
        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query, per_page=per_page)
        objects, has_next = paginator.page(page)
        data = {'objects': objects, 'page': page, 'has_next': has_next, 'has_previous': page > 1}
        self.render_template('admin/counters.html', data)

    def post(self):
        cntx = ndb.get_context()
        cntx.set_cache_policy(False)
        if self.request.POST.get('action:delete'):
            key = ndb.Key(urlsafe=self.request.POST.get('action:delete'))
            key.delete()
        elif self.request.POST.get('action:edit'):
            input_id = self.request.POST.get('action:edit')
            key = ndb.Key(urlsafe=input_id)
            obj = key.get()
            obj.count = int(self.request.POST.get('count.%s' % input_id))
            obj.put()

        self.redirect('/admin/counters')