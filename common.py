from __future__ import division
import os
import math
import hashlib
import datetime
import itertools
import collections
import logging
import traceback
from operator import itemgetter
from datetime import timedelta

import webapp2
import jinja2
from webapp2_extras import i18n, sessions
from webapp2_extras.i18n import gettext, ngettext, lazy_gettext as _
from webapp2_extras.jinja2 import get_jinja2
from jinja2.filters import environmentfilter, do_mark_safe
from google.appengine.api import users, memcache, search
from google.appengine.ext import ndb

from wtforms import widgets, fields
from cloud import calculate_cloud
from models import INDEX, Counter, Photo
from settings import DEVEL, COLORS, FAMILY, PER_PAGE, TIMEOUT, LANGUAGE_COOKIE_NAME


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
    if memcache.get(key):
        return True
    else:
        return False


def boolimage(value):
    """ {{ object.key.name|incache:"small"|yesno:"yes,no"|boolimage }} """
    if value is True:
        return do_mark_safe('<img src="/static/images/icon_yes.png" alt="%s"/>' % value)
    else:
        return do_mark_safe('<img src="/static/images/icon_no.png" alt="%s"/>' % value)


@environmentfilter
def css_classes(env, classes):
    return u' '.join(unicode(x) for x in classes if x) or env.undefined(hint='No classes requested')


def filesizeformat(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and "KiB" or "kB"),
        (binary and "MiB" or "MB"),
        (binary and "GiB" or "GB"),
        (binary and "TiB" or "TB"),
        (binary and "PiB" or "PB"),
        (binary and "EiB" or "EB"),
        (binary and "ZiB" or "ZB"),
        (binary and "YiB" or "YB")
    ]
    if bytes == 1:
        return "1 Byte"
    elif bytes < base:
        return "%d Bytes" % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if bytes < unit:
                return '%.1f %s' % ((base * bytes / unit), prefix)
        return '%.1f %s' % ((base * bytes / unit), prefix)


def timesince_jinja(d, now=None):
    # http://stackoverflow.com/questions/8292477/localized-timesince-filter-for-jinja2-with-gae
    chunks = (
        (60 * 60 * 24 * 365, lambda n: ngettext('year', 'years', n)),
        (60 * 60 * 24 * 30, lambda n: ngettext('month', 'months', n)),
        (60 * 60 * 24 * 7, lambda n: ngettext('week', 'weeks', n)),
        (60 * 60 * 24, lambda n: ngettext('day', 'days', n)),
        (60 * 60, lambda n: ngettext('hour', 'hours', n)),
        (60, lambda n: ngettext('minute', 'minutes', n))
    )
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now()

    delta = now - (d - timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        return u'0 ' + gettext('minutes')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    s = gettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    if i + 1 < len(chunks):
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += gettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
    return s


ENV.globals.update({
    'now': now,
    'version': version,
    'gaesdk': gaesdk,
    'language': language,
    'uri_for': webapp2.uri_for,
})
ENV.filters.update({
    'incache': incache,
    'boolimage': boolimage,
    'format_date': format_date,
    'format_datetime': format_datetime,
    'image_url_by_num': image_url_by_num,
    'css_classes': css_classes,
    'filesizeformat': filesizeformat,
    'timesince': timesince_jinja,
})

real_handle_exception = ENV.handle_exception


def handle_exception(self, *args, **kwargs):
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
        memcache.set(key, content, TIMEOUT * 12)
    return content


def count_property(kind, field):
    prop = field
    if field == 'date':
        prop = 'year'
    key = '%s_%s' % (kind, field)
    # TODO REMEMBER
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
    memcache.set(key, content, TIMEOUT * 12)
    return content


def count_colors():
    key = 'Photo_colors'
    content = memcache.get(key)
    if content is None:
        content = []
        for k, d in COLORS.items():
            if d['field'] == 'hue':
                query = Photo.query(Photo.hue == d['name'], Photo.sat == 'color').order(-Photo.date)
            elif d['field'] == 'lum':
                query = Photo.query(Photo.lum == d['name'], Photo.sat == 'monochrome').order(-Photo.date)
            data = COLORS[k]
            data.update({'count': query.count(1000)})
            content.append(data)
        content = sorted(content, key=itemgetter('order'))
        memcache.set(key, content, TIMEOUT * 12)
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
            # TODO Not all emails are gmail
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
        return '%s/%s/' % (self.field, self.value)


class Paginator:
    timeout = TIMEOUT / 6

    def __init__(self, query, per_page=PER_PAGE):
        self.query = query
        self.per_page = per_page
        self.id = hashlib.md5(repr(self.query)).hexdigest()
        self.cache = memcache.get(self.id)

        if self.cache is None:
            self.cache = {0: None}
            memcache.add(self.id, self.cache, self.timeout)

    def pagekeys(self, num):
        if num < 1: webapp2.abort(404)

        try:
            cursor = self.cache[num - 1]
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, start_cursor=cursor)
        except KeyError:
            offset = (num - 1) * self.per_page
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, offset=offset)

        if not keys:
            return keys, False

        if keys and cursor:
            self.cache[num] = cursor
            memcache.replace(self.id, self.cache, self.timeout)
            return keys, has_next
        else:
            webapp2.abort(404)

    def page(self, num):
        keys, has_next = self.pagekeys(num)
        return ndb.get_multi(keys), has_next

    def triple(self, idx):
        """ num and idx are 1 base index """
        none = ndb.Key('XXX', 'xxx')
        rem = idx % self.per_page
        num = int(idx / self.per_page) + (0 if rem == 0 else 1)
        keys, has_next = self.pagekeys(num)

        if rem == 1:
            if num == 1:
                collection = [none] + keys + [none]
            else:
                other, x = self.pagekeys(num - 1)
                collection = (other + keys + [none])[idx - (num - 2) * self.per_page - 2:]
        else:
            if has_next:
                other, x = self.pagekeys(num + 1)
            else:
                other = [none]
            collection = (keys + other)[idx - (num - 1) * self.per_page - 2:]

        prev, obj, next = ndb.get_multi(collection[:3])
        return num, prev, obj, next


class SearchPaginator:
#    timeout = 60 #TIMEOUT/10
    def __init__(self, querystring, per_page=PER_PAGE):
        self.querystring = querystring
        # '"{0}"'.format(querystring.replace('"',''))
        self.per_page = per_page

    #        self.id = hashlib.md5(querystring).hexdigest()
    #        self.cache = memcache.get(self.id)
    #
    #        if self.cache is None:
    #            self.cache = {1: None}
    #            memcache.add(self.id, self.cache, self.timeout)

    def page(self, num):
        error = None
        results = []
        number_found = 0
        has_next = False
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
                offset=(num - 1) * self.per_page,
                returned_fields=['headline', 'author', 'tags', 'date', 'link', 'kind'],
                snippeted_fields=['body']
            ))
        try:
            found = INDEX.search(query)
            results = found.results
            number_found = found.number_found
        except Exception, error:
            found = []
        else:
            if number_found > 0:
                has_next = number_found > num * self.per_page
                #            self.cache[num + 1] = found.cursor.web_safe_string
                #            memcache.replace(self.id, self.cache, self.timeout)

        return results, number_found, has_next, error


class ListPaginator:
    def __init__(self, objects, per_page=PER_PAGE):
        self.objects = objects
        self.per_page = per_page
        self.count = len(self.objects)
        self.num_pages = int(math.ceil(self.count / self.per_page))

    def page(self, num):
        if num < 1:
            webapp2.abort(404)

        offset = (num - 1) * self.per_page
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
        self.choices = [(users.User(x).nickname(), x) for x in FAMILY]


class TagsField(fields.TextField):
    widget = widgets.TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = sorted([x.strip().lower() for x in valuelist[0].split(',') if x.strip() != ''])
        else:
            self.data = []


def sign_helper(request):
    forbidden = ('admin', '403', 'addcomment')
    referer = request.headers.get('Referer', webapp2.uri_for('start'))
    if referer.endswith(forbidden):
        referer = webapp2.uri_for('start')
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
        return get_jinja2(app=self.app)

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
        self.response.write(template.render(kwargs))


class SetLanguage(BaseHandler):
    def post(self):
        next = self.request.headers.get('Referer', webapp2.uri_for('start'))
        response = self.redirect(next)
        lang_code = self.request.get('language', None)

        if lang_code:
            if hasattr(self, 'session'):
                self.session[LANGUAGE_COOKIE_NAME] = lang_code
            else:
                self.request.headers['Cookie'] = '%s=%s' % (LANGUAGE_COOKIE_NAME, lang_code)
        return response