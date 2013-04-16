__author__ = 'milan'

import os
import json
import sys
import traceback
import logging
from datetime import datetime, timedelta
from operator import itemgetter

import webapp2
import jinja2
from webapp2_extras import i18n, sessions
from webapp2_extras.i18n import gettext, ngettext
from webapp2_extras.appengine.users import login_required
from webapp2_extras.jinja2 import get_jinja2
from jinja2.filters import environmentfilter, do_mark_safe, do_striptags
from google.appengine.api import users, memcache
from google.appengine.ext import ndb
from common import SearchPaginator
from models import Cloud

from settings import DEVEL, TEMPLATE_DIR, LANGUAGES, RESULTS


def version():
    return os.environ.get('CURRENT_VERSION_ID').split('.').pop(0)


def gaesdk():
    return os.environ.get('SERVER_SOFTWARE')


def language(code):
    return code.split('_')[0]


def now():
    date = datetime.now()
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
    """ {{ object.key.name|incache|boolimage }} """
    if value is True:
        return do_mark_safe('<i class="icon-ok-sign" style="color: #060"></i>')
    else:
        return do_mark_safe('<i class="icon-minus-sign" style="color: #c00"></i>')


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
    if not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime):
        now = datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.now()

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


def to_json(value):
    # http://stackoverflow.com/questions/8727349/converting-dict-object-to-string-in-django-jinja2-template
    return do_mark_safe(json.dumps(value))


def split(value, sep=','):
    if value:
        return value.split(sep)
    return []

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
    'to_json': to_json,
    'split': split,
})

real_handle_exception = ENV.handle_exception


def handle_exception(self, *args, **kwargs):
    logging.error('Template exception:\n%s', traceback.format_exc())
    real_handle_exception(self, *args, **kwargs)


ENV.handle_exception = handle_exception


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def dispatch(self):
        try:
            super(BaseHandler, self).dispatch()
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def user(self):
        return users.get_current_user()

    @webapp2.cached_property
    def is_admin(self):
        return users.is_current_user_admin()

    @webapp2.cached_property
    def jinja2(self):
        return get_jinja2(app=self.app)

    def handle_exception(self, exception, debug):
        template = ENV.get_template('errors/default.html')
        if isinstance(exception, webapp2.HTTPException):
            data = {'error': exception, 'path': self.request.path_qs}
            self.render_template(template, data)
            self.response.set_status(exception.code)
        else:
            data = {'error': exception, 'lines': ''.join(traceback.format_exception(*sys.exc_info()))}
            self.render_template(template, data)
            self.response.set_status(500)

    def render_template(self, filename, kwargs):
        lang_code = self.session.get('lang_code') or 'en_US'
        i18n.get_i18n().set_locale(lang_code)

        context = {
            'LANGUAGE_CODE': lang_code,
            'LANGUAGES': LANGUAGES,
            'user': self.user,
            'is_admin': self.is_admin,
            'devel': DEVEL
        }
        if 'headers' in kwargs:
            self.response.headers = kwargs['headers']
            del kwargs['headers']
        kwargs.update(context)
        template = ENV.get_template(filename)
        self.response.write(template.render(kwargs))

    def render_json(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        self.response.write(json.dumps(data))


class RenderCloud(BaseHandler):
    def get(self, mem_key, value=None):
        kind, field = mem_key.split('_')
        items = Cloud(mem_key).get_list()

        if field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
            items = sorted(items, key=itemgetter('count'), reverse=True)[:10]

        if field == 'date':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        elif field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso', 'forkind',):
            items = sorted(items, key=itemgetter('name'), reverse=False)
        elif field == 'color':
            items = sorted(items, key=itemgetter('order'))

        self.render_template(
            'snippets/cloud.html', {
                'items': items,
                'link': '%s_filter_all' % kind.lower(),
                'field_name': field,
                'filter': {'field': field, 'value': value} if (field and value) else None})


class RenderGraph(BaseHandler):
    def get(self, mem_key):
        kind, field = mem_key.split('_')
        items = Cloud(mem_key).get_list()

        if field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
            items = sorted(items, key=itemgetter('count'), reverse=True)[:10]

        if field == 'date':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        elif field in ('eqv', 'iso', 'forkind',):
            items = sorted(items, key=itemgetter('name'), reverse=False)
        elif field == 'color':
            items = sorted(items, key=itemgetter('order'))

        self.render_template('snippets/graph.html', {'items': items, 'field_name': field})


class Find(BaseHandler):
    def get(self):
        querystring = self.request.get('find')
        page = int(self.request.get('page', 1))
        paginator = SearchPaginator(querystring, per_page=RESULTS)
        results, number_found, has_next, error = paginator.page(page)

        objects = []
        for doc in results:
            f = dict()
            key = ndb.Key(urlsafe=doc.doc_id)
            if key.parent():
                link = webapp2.uri_for(key.parent().kind().lower(), slug=key.parent().string_id())
            else:
                try:
                    link = webapp2.uri_for(key.kind().lower(), slug=key.string_id())
                except KeyError:
                    link = ''  # Comment.is_message

            f['kind'] = key.kind()
            f['link'] = link
            for field in doc.fields:
                f[field.name] = field.value
            for expr in doc.expressions:
                f[expr.name] = do_striptags(expr.value)
            objects.append(f)

        self.render_template('results.html',
                             {'objects': objects, 'phrase': querystring, 'number_found': number_found,
                              'page': page, 'has_next': has_next, 'has_previous': page > 1, 'error': error})


class DeleteHandler(BaseHandler):
    @login_required
    def get(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        if key.parent():
            next = self.request.headers.get('Referer', webapp2.uri_for('start'))
        else:
            next = webapp2.uri_for('%s_all' % key.kind().lower())

        obj = key.get()
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                webapp2.abort(403)
        data = {'object': obj, 'post_url': self.request.path, 'next': next}
        self.render_template('snippets/confirm.html', data)

    def post(self, safe_key):
        next = str(self.request.get('next'))
        key = ndb.Key(urlsafe=safe_key)
        key.delete()
        self.redirect(next)


class SetLanguage(BaseHandler):
    def post(self):
        next = self.request.headers.get('Referer', webapp2.uri_for('start'))
        lang_code = self.request.get('language', None)
        if lang_code:
            self.session['lang_code'] = lang_code
        self.redirect(next)


class Sign(BaseHandler):
    def get(self):
        referer = self.request.headers.get('Referer', webapp2.uri_for('start'))
        if referer.endswith('admin/'):
            referer = webapp2.uri_for('start')
        if users.get_current_user():
            dest_url = users.create_logout_url(referer)
        else:
            dest_url = users.create_login_url(referer)
        self.redirect(dest_url)