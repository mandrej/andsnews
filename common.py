import os, webapp2, jinja2, colorsys
import math, hashlib
import itertools, collections
import datetime, time
from webapp2_extras import i18n, sessions
from webapp2_extras.i18n import lazy_gettext as _
from operator import itemgetter
from google.appengine.api import images, users, taskqueue, memcache, search
from google.appengine.ext import ndb, deferred
from cloud import calculate_cloud
from models import Counter, Photo, INDEX
import logging

LANGUAGES = (
    ('en', _('english')),
    ('sr', _('serbian')),
)
LANGUAGE_COOKIE_NAME = 'ands_lang'
TIMEOUT = 3600 # 1 hour
PER_PAGE = 12
LIMIT = 1024*1024
ADMIN_JID = 'milan.andrejevic@gmail.com'

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.i18n'],
    autoescape=True
)
ENV.install_gettext_translations(i18n, newstyle=False)
ENV.install_gettext_callables(
    lambda x: i18n.gettext(x),
    lambda s, p, n: i18n.ngettext(s, p, n),
    newstyle=False)


def version():
    return os.environ.get('CURRENT_VERSION_ID').split('.').pop(0)

def gaesdk():
    return os.environ.get('SERVER_SOFTWARE')

def now():
    date = datetime.datetime.now()
    return date.strftime('%Y')

ENV.globals.update({
    'now': now,
    'version': version,
    'gaesdk': gaesdk,
})
ENV.filters.update({
    'format_date': i18n.format_date,
    'format_time': i18n.format_time,
    'format_datetime': i18n.format_datetime,
    'format_timedelta': i18n.format_timedelta,
    })

HUE = [
    {'span': map(lambda x: x+360 if x<0 else x, xrange(-10, 10)), 'order': '0', 'name': 'red', 'hex': '#cc0000'}, # 0
    {'span': xrange(10, 40), 'order': '1', 'name': 'orange', 'hex': '#ff7f00'}, # 30
    {'span': xrange(40, 60), 'order': '2', 'name': 'yellow', 'hex': '#ffff0f'}, # 60
    {'span': xrange(60, 150), 'order': '3', 'name': 'green', 'hex': '#00bf00'}, # 120
    {'span': xrange(150, 190), 'order': '4', 'name': 'teal', 'hex': '#00bfbf'}, # 180
    {'span': xrange(190, 240), 'order': '5', 'name': 'blue', 'hex': '#005fbf'}, # 210
    {'span': xrange(240, 290), 'order': '6', 'name': 'purple', 'hex': '#5f00bf'}, # 270
    {'span': xrange(290, 350), 'order': '7', 'name': 'pink', 'hex': '#bf005f'} # 330
]
LUM = [
    {'span': xrange(0, 10), 'order': '8', 'name': 'dark', 'hex': '#191919'},
    {'span': xrange(10, 40), 'order': '9', 'name': 'medium', 'hex': '#4c4c4c'},
    {'span': xrange(40, 101), 'order': 'a', 'name': 'light', 'hex': '#cccccc'}
]
SAT = [
    {'span': xrange(0, 10), 'name': 'monochrome'},
    {'span': xrange(10, 101), 'name': 'color'}
]

COLORS = {}
for x in HUE:
    COLORS['hue-%s' % x['name']] = {'hex': x['hex'], 'field': 'hue', 'name': x['name'], 'order': x['order']}

for x in LUM:
    COLORS['lum-%s' % x['name']] = {'hex': x['hex'], 'field': 'lum', 'name': x['name'], 'order': x['order']}

def median(buff):
    triple = []
    histogram = images.histogram(buff)
    for band in histogram:
        suma = 0
        limit = sum(band)/2
        for i in xrange(256):
            suma += band[i]
            if (suma > limit):
                triple.append(i)
                break
    return triple

def range_names(rgb):
    def in_range(value, component):
        for x in component:
            if value in x['span']:
                return x['name']

    rel_rgb = map(lambda x: x/255, rgb)
    h, l, s = colorsys.rgb_to_hls(*rel_rgb)
    H, L, S = int(h*360), int(l*100), int(s*100)
    hue = in_range(H, HUE)
    lum = in_range(L, LUM)
    sat = in_range(S, SAT)
    return hue, lum, sat

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
        memcache.set(key, content, TIMEOUT*12)
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
    memcache.set(key, content, TIMEOUT*12)
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
        memcache.set(key, content, TIMEOUT*12)
    return content

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
#        TODO Not all emails are gmail
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

class Paginator:
    timeout = TIMEOUT/6
    def __init__(self, query, per_page=PER_PAGE):
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
            webapp2.abort(404)
        if num > self.num_pages:
            if num == 1 and self.count == 0:
                pass
            else:
                webapp2.abort(404)

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
#    timeout = 60 #TIMEOUT/10
    def __init__(self, querystring, per_page=PER_PAGE):
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
    def __init__(self, objects, per_page=PER_PAGE):
        self.objects = objects
        self.per_page = per_page
        self.count = len(self.objects)
        self.num_pages = int(math.ceil(self.count/self.per_page))

    def page(self, num):
        if num < 1:
            webapp2.abort(404)

        offset = (num - 1)*self.per_page
        results = self.objects[offset: offset + self.per_page]
        has_next = num < self.num_pages
        return results, has_next

def get_language_from_request(self, request):
    """
    Analyzes the request to find what language the user wants the system to
    show. If the user requests a sublanguage where we have a main language, we send
    out the main language.
    """
    if self.session:
        lang_code = self.session.get('i18n_language', None)
        if lang_code:
            logging.info('language found in session')
            return lang_code

    lang_code = request.COOKIES.get(LANGUAGE_COOKIE_NAME)
    if lang_code:
        logging.info('language found in cookies')
        return lang_code

    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    for accept_lang, unused in self.parse_accept_lang_header(accept):
        logging.info('accept_lang:'+accept_lang)
        lang_code = accept_lang

    return lang_code

class BaseHandler(webapp2.RequestHandler):
#    def dispatch(self):
#        # Get a session store for this request.
#        self.session_store = sessions.get_store(request=self.request)
#
#        try:
#            # Dispatch the request.
#            webapp2.RequestHandler.dispatch(self)
#        finally:
#            # Save all sessions.
#            self.session_store.save_sessions(self.response)
#
#    @webapp2.cached_property
#    def session(self):
#        # Returns a session using the default cookie key.
#        return self.session_store.get_session()

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, template_values, **template_args):
        language_code = 'en_US'
        i18n.get_i18n().set_locale(language_code)
        template_values['LANGUAGE_CODE'] = language_code
        template_values['LANGUAGES'] = LANGUAGES
#        get_language_from_request(self, self.request)
#        logging.error(self.request)
        template = ENV.get_template(filename)
        self.response.out.write(template.render(template_values))