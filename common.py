from __future__ import division
import os, re, webapp2, jinja2, colorsys
import math, hashlib
import itertools, collections
import datetime
from webapp2_extras import i18n, sessions
from webapp2_extras.i18n import lazy_gettext as _
from operator import itemgetter
from google.appengine.api import images, users, memcache, search
from google.appengine.ext import ndb, deferred
from google.appengine.runtime import apiproxy_errors
from wtforms import Form, widgets, fields, validators
from cloud import calculate_cloud
from models import Counter, Photo, INDEX, median, range_names
from settings import DEVEL, HUE, LUM, SAT, COLORS, FAMILY, PER_PAGE, TIMEOUT, LANGUAGE_COOKIE_NAME

LANGUAGES = (
    ('en_US', _('english')),
    ('sr_RS', _('serbian')),
)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.i18n', 'jinja2.ext.with_'],
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

def language(code):
    return code.split('_')[0]

def now():
    date = datetime.datetime.now()
    return date.strftime('%Y')

def format_date(value, format='%Y-%m-%d'):
    return value.strftime(format)

def format_datetime(value, format='%Y-%m-%dT%H:%M:%S'):
    return value.strftime(format)

def image_url_by_num(obj, arg):
    """ {{ object|image_url_by_num:form.initial.ORDER }}/small
        {{ object|image_url_by_num:object.front }}/small """
    return obj.image_url(arg)

def incache(key):
    if memcache.get(key): return True
    else: return False

ENV.globals.update({
    'now': now,
    'version': version,
    'gaesdk': gaesdk,
    'language': language,
    'incache': incache,
})
ENV.filters.update({
    'format_date': format_date,
    'format_datetime': format_datetime,
    'image_url_by_num': image_url_by_num
})

real_handle_exception = ENV.handle_exception
def handle_exception(self, *args, **kwargs):
    import logging, traceback
    logging.error('Template exception:\n%s', traceback.format_exc())
    real_handle_exception(self, *args, **kwargs)
ENV.handle_exception = handle_exception

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

def make_thumbnail(kind, slug, size, mime='image/jpeg'):
    if kind == 'Photo':
        if size == 'small': _width = 240
        obj = ndb.Key('Photo', slug, 'Picture', slug).get()
    elif kind == 'Entry':
        if size == 'small': _width = 60
        m = re.match(r'(.+)_\d', slug)
        obj = ndb.Key('Entry', m.group(1), 'Img', slug).get()
        mime = str(obj.mime)

    if obj is None:
        webapp2.abort(404)
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
                    photo.hue, photo.lum, photo.sat = range_names(obj.rgb)
                    photo.put()
                obj.put()
        return out, mime
    else:
        return buff, mime

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

class EmailField(fields.SelectField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)
        user = users.get_current_user()
        email = user.email()
        if not email in FAMILY:
            FAMILY.append(email)
        self.choices = [(x, x) for x in FAMILY]

class TagsField(fields.TextField):
    widget = widgets.TextInput()
    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = sorted([x.strip().lower() for x in valuelist[0].split(',')])
        else:
            self.data = []

FORBIDDEN = ('admin', '403', 'addcomment')
def sign_helper(request):
    referer = request.headers.get('Referer', '/')
    if referer.endswith(FORBIDDEN):
        referer = '/'
    if users.get_current_user():
        dest_url = users.create_logout_url(referer)
    else:
        dest_url = users.create_login_url(referer)
    return webapp2.redirect(dest_url)

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, kwargs):
        lang_code = self.session.get(LANGUAGE_COOKIE_NAME) or self.request.cookies.get(LANGUAGE_COOKIE_NAME) or 'en_US'
        i18n.get_i18n().set_locale(lang_code)
        context = {
            'LANGUAGE_CODE': lang_code,
            'LANGUAGES': LANGUAGES,
            'user': users.get_current_user(),
            'is_admin': users.is_current_user_admin(),
            'devel': DEVEL
        }
        kwargs.update(context)
        template = ENV.get_template(filename)
        self.response.out.write(template.render(kwargs))

class SetLanguage(BaseHandler):
    def post(self):
        next = self.request.headers.get('Referer', '/')
        response = self.redirect(next)
        lang_code = self.request.POST.get('language', None)

        if lang_code:
            if hasattr(self, 'session'):
                self.session[LANGUAGE_COOKIE_NAME] = lang_code
            else:
                self.request.headers['Cookie'] = '%s=%s' % (LANGUAGE_COOKIE_NAME, lang_code)
        return response