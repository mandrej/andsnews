from __future__ import division
import re, math
import datetime, time
import json, hashlib, threading
import itertools, collections
from operator import itemgetter
from functools import wraps
from google.appengine.api import images, users, taskqueue, memcache, search
from google.appengine.ext import ndb, deferred
from google.appengine.runtime import apiproxy_errors
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.utils.translation import gettext_lazy as _
from models import INDEX, Counter, Photo, HUE, LUM, range_names, median
from cloud import calculate_cloud
from django.conf import settings

COLORS = {}
for x in HUE:
    COLORS['hue-%s' % x['name']] = {'hex': x['hex'], 'field': 'hue', 'name': x['name'], 'order': x['order']}

for x in LUM:
    COLORS['lum-%s' % x['name']] = {'hex': x['hex'], 'field': 'lum', 'name': x['name'], 'order': x['order']}

def make_cloud(kind, field):
    key = '%s_%s' % (kind, field)
    content = memcache.get(key)
    if content is None:
        coll = {}
        query = Counter.query(Counter.forkind == kind, Counter.field == field)
        for counter in query:
            count = counter.count
            if count > 0:
                try:
                    # keep sorted date, eqv, iso by int
                    coll[int(counter.value)] = count
                except ValueError:
                    coll[counter.value] = count
        content = calculate_cloud(coll)
        memcache.set(key, content, settings.TIMEOUT*12)
    return content

def count_property(kind, field):
    prop = field
    if field == 'date':
        prop = 'year'
    key = '%s_%s' % (kind, field)
    model = ndb.Model._kind_map.get(kind)
    query = model.query()
    properties = [getattr(x, prop, None) for x in query]
    if prop == 'tags':
        properties = list(itertools.chain(*properties))
    elif prop == 'author':
        properties = [x.nickname() for x in properties]
    tally = collections.Counter(filter(None, properties))
    
    for value, count in tally.items():
        keyname = '%s||%s||%s' % (kind, field, value)
        params = dict(zip(('forkind', 'field', 'value'), map(str, [kind, field, value])))
        obj = Counter.get_or_insert(keyname, **params)
        if obj.count != count:
            obj.count = count
            obj.put()
    
    coll = dict(tally.items())
    content = calculate_cloud(coll)
    memcache.set(key, content, settings.TIMEOUT*12)
    return content

def count_colors():
    key = 'Photo_colors'
    content = memcache.get(key)
    if content is None:
        content = []
        for k, d in COLORS.items():
            if d['field'] == 'hue':
                query = Photo.query(Photo.hue == d['name'], Photo.sat == 'color').order(-Photo.date)
                count = query.count(1000)
            elif d['field'] == 'lum':
                query = Photo.query(Photo.lum == d['name'], Photo.sat == 'monochrome').order(-Photo.date)
                count = query.count(1000)
            data = COLORS[k]
            data.update({'count': count})
            content.append(data)
        content = sorted(content, key=itemgetter('order'))
        memcache.set(key, content, settings.TIMEOUT*12)
    return content

def make_thumbnail(kind, slug, size, mime='image/jpeg'):
    if kind == 'Photo':
        if size == 'small': _width = 240
        obj = ndb.Key('Photo', slug, 'Picture', slug).get()
    elif kind == 'Entry':
        if size == 'small': _width = 60
        m = re.match(r'(.+)_\d', slug)
        obj = ndb.Key('Entry', m.group(1), 'Img', slug).get()
        mime = obj.mime
    
    if obj is None:
        raise Http404
    buff = obj.blob
    if size == 'normal': return buff, mime
    if size == 'small' and obj.small is not None: return obj.small, mime
    img = images.Image(buff)

    aspect = img.width/img.height
    if aspect < 1:
        aspect = 1/aspect
    _thumb = int(math.ceil(_width*aspect))

    if _thumb < img.width or _thumb < img.height:
        if size == 'small':
            img.resize(_thumb, _thumb)
        else:
            img.resize(_width, _thumb)
        try:
            if mime == 'image/png':
                out = img.execute_transforms(output_encoding=images.PNG)
            else:
                out = img.execute_transforms(output_encoding=images.JPEG)
        except apiproxy_errors.OverQuotaError:
            deferred.defer(make_thumbnail, kind, slug, size)
            return None, mime
        else:
            if size== 'small' and obj.small is None:
                obj.small = out
                if kind == 'Photo':
                    obj.rgb = median(out)
                    obj.put()
                    photo = obj.key.parent().get()
                    photo.hue, photo.lum, photo.sat = range_names(*obj.hls)
                    photo.put()
                obj.put()
        return out, mime
    else:
        return buff, mime

class Cache:
    def __init__(self, size=100):
        if int(size) < 1:
            raise AttributeError('size < 1 or not a number')
        self.size = size
        self.dict = collections.OrderedDict()
        self.lock = threading.Lock()

    def __getitem__(self, key):
        with self.lock:
            return self.dict[key]

    def __setitem__(self, key, value):
        with self.lock:
            while len(self.dict) >= self.size:
                self.dict.popitem(last=False)
            self.dict[key]=value

    def __delitem__(self, key):
        with self.lock:
            del self.dict[key]

#search_cache = Cache(size=10)

class Filter:
    def __init__(self, field, value):
        self.field, self.value = field, value
        try:
            assert (self.field and self.value)
        except AssertionError:
            self.empty = True
        else:
            self.empty = False

    @property
    def parameters(self):
        if self.empty: return {}
        if self.field == 'date':
            return {'year': int(self.value)}
        elif self.field == 'author':
#            TODO Not all emails are gmail
            return {'author': users.User(email='%s@gmail.com' % self.value)}
        elif self.field == 'forkind':
            return {'forkind': self.value.capitalize()}
        elif self.field == 'hue':
            return {'hue': self.value, 'sat': 'color'}
        elif self.field == 'lum':
            return {'lum': self.value, 'sat': 'monochrome'}
        else:
            try:
                self.value = int(self.value)
            except ValueError:
                pass
            return {'%s' % self.field: self.value}

    @property
    def title(self):
        if self.empty: return ''
        if self.field == 'forkind':
            if self.value == 'entry':
                return '/ %s' % _('for blogs')
            elif self.value == 'photo':
                return '/ %s' % _('for photos')
            else:
                return '/ %s' % _('messages')
        elif self.field == 'eqv':
            return '/ %s mm' % self.value
        elif self.field == 'iso':
            return '/ %s ASA' % self.value
        elif self.field in ('hue', 'lum'):
            return '/ %s' % _(self.value)
        else:
            return '/ %s' % self.value

    @property
    def url(self):
        if self.empty: return ''
        return '/%s/%s' % (self.field, self.value)

FORBIDDEN = ('admin', '403', 'addcomment')
def sign_helper(request):
    referer = request.META.get('HTTP_REFERER', '/')
    if referer.endswith(FORBIDDEN):
        referer = '/'
    if users.get_current_user():
        dest_url = users.create_logout_url(referer)
    else:
        dest_url = users.create_login_url(referer)
    return redirect(dest_url)

def login_required(viewfunc):
    @wraps(viewfunc)
    def _checklogin(request, *args, **kwargs):
        if users.get_current_user():
            return viewfunc(request, *args, **kwargs)
        return redirect(users.create_login_url(request.path))
    return _checklogin

def admin_required(viewfunc):
    @wraps(viewfunc)
    def _checklogin(request, *args, **kwargs):
        if users.is_current_user_admin():
            return viewfunc(request, *args, **kwargs)
        return redirect(users.create_login_url(request.path))
    return _checklogin

class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, ndb.Model):
            return dict((p, getattr(obj, p)) for p in obj.properties())
        elif isinstance(obj, users.User):
            return obj.email()
        return obj

class json_response(HttpResponse):
    def __init__(self, data):
        HttpResponse.__init__(
            self, json.dumps(data, cls=LazyEncoder),
            mimetype='application/json')

class Paginator:
    timeout = settings.TIMEOUT/6
    def __init__(self, query, per_page=settings.PER_PAGE):
        self.query = query
        self.per_page = per_page
        self.id = hashlib.md5(repr(self.query)).hexdigest()
        self.cache = memcache.get(self.id)
        
        if self.cache is None:
            self.query._keys_only = True
            self.count = self.query.count(1000)
            if self.count == 0:
                self.num_pages = 0
            else:
                self.num_pages = int(math.ceil(self.count/self.per_page))
            
            self.cache = {'count': self.count, 'num_pages': self.num_pages, 0: None}
            memcache.add(self.id, self.cache, self.timeout)
        else:
            self.count = self.cache['count']
            self.num_pages = self.cache['num_pages']
    
    def page(self, num):
        if num < 1:
            raise Http404
        if num > self.num_pages:
            if num == 1 and self.count == 0:
                pass
            else:
                raise Http404
        
        self.query._keys_only = False
        try:
            cursor = self.cache[num - 1]
            results, cursor, has_next = self.query.fetch_page(self.per_page, start_cursor=cursor)
        except KeyError:
            offset = (num - 1)*self.per_page
            results, cursor, has_next = self.query.fetch_page(self.per_page, offset=offset)
            
        self.cache[num] = cursor
        memcache.replace(self.id, self.cache, self.timeout)
        return results, has_next
    
    def triple(self, num, idx):
        objects, has_next = self.page(num)
        if num == 1 and idx == 1:
            collection = [None] + objects
            numbers = {'prev': [], 'next': [num, idx + 1]}
        elif num > 1 and idx == 1:
            other, has_next = self.page(num - 1)
            collection = (other + objects)[self.per_page + idx - 2:]
            numbers = {'prev': [num - 1, self.per_page], 'next': [num, idx + 1]}
        elif idx == len(objects):
            if has_next:
                other, has_next = self.page(num + 1)
                collection = (objects + other)[idx - 2:]
                numbers = {'prev': [num, idx - 1], 'next': [num + 1, 1]}
            else:
                collection = objects[idx - 2:] + [None]
                numbers = {'prev': [num, idx - 1], 'next': []}
        else:
            collection = objects[idx - 2:]
            numbers = {'prev': [num, idx - 1], 'next': [num, idx + 1]}
        
        try:
            previous, obj, next = collection[:3]
        except ValueError:
            previous, obj = collection[:2]
            next = None
        
        return previous, obj, next, numbers

class SearchPaginator:
#    timeout = 60 #settings.TIMEOUT/10
    def __init__(self, querystring, per_page=settings.PER_PAGE):
        self.querystring = querystring #'"{0}"'.format(querystring.replace('"',''))
        self.per_page = per_page
#        self.id = hashlib.md5(querystring).hexdigest()
#        self.cache = memcache.get(self.id)
#        
#        if self.cache is None:
#            self.cache = {1: None}
#            memcache.add(self.id, self.cache, self.timeout)
    
    def page(self, num):
        has_next= False
#        opts = {
#            'limit': self.per_page,
#            'returned_fields': ['headline', 'author', 'tags', 'date', 'link', 'kind'],
#            'returned_expressions': [search.FieldExpression(name='body', expression='snippet("%s", body)' % self.querystring)]
#            'snippeted_fields': ['body']
#        }
#        try:
#            cursor = self.cache[num]
#        except KeyError:
#            cursor = None
#        
#        opts['cursor'] = search.Cursor(web_safe_string=cursor)
#        opts['offset'] = (num - 1)*self.per_page
#        found = INDEX.search(search.Query(query_string=self.querystring,
#                                          options=search.QueryOptions(**opts)))
        query = search.Query(
            query_string=self.querystring,
            options=search.QueryOptions(
                    limit=self.per_page,
                    offset=(num - 1)*self.per_page,
                    returned_fields=['headline', 'author', 'tags', 'date', 'link', 'kind', 'body'],
        ))
        
        found = INDEX.search(query)
        if found.number_found > 0:
            has_next = found.number_found > num*self.per_page
#            self.cache[num + 1] = found.cursor.web_safe_string
#            memcache.replace(self.id, self.cache, self.timeout)
        
        return found.results, found.number_found, has_next

class ListPaginator:
    def __init__(self, objects, per_page=settings.PER_PAGE):
        self.objects = objects
        self.per_page = per_page
        self.count = len(self.objects)
        self.num_pages = int(math.ceil(self.count/self.per_page))

    def page(self, num):
        if num < 1:
            raise Http404

        offset = (num - 1)*self.per_page
        results = self.objects[offset: offset + self.per_page]
        has_next = num < self.num_pages
        return results, has_next
    
def error404(request, tmpl='404.html'):
    path = request.path
    qs = request.META.get('QUERY_STRING', None)
    if qs:
        path += '?%s' % qs
        
    return render(request, tmpl, {'request_path': path}, status=404)

def error500(request, tmpl='500.html'):
    if not settings.DEVEL:
        exclude = re.compile('bot', re.IGNORECASE)
        ua = request.META['HTTP_USER_AGENT']
        remote = request.META.get('REMOTE_HOST', '')
        if not re.findall(exclude, ua):
            stamp = time.strftime('%I:%M %p on %A', datetime.datetime.now().timetuple())
            message = "%s\n%s\n%s" % (stamp, request.path, remote)
            taskqueue.Task(url='/send', countdown=60, params={'msg': message}).add(queue_name='errors')

    return render(request, tmpl, status=500)
