from __future__ import division

import json
import datetime
import sys
import traceback
import hashlib
import uuid
import logging
from operator import itemgetter

import webapp2
from jinja2.filters import Markup
from webapp2_extras import i18n, sessions, jinja2
from webapp2_extras.appengine.users import login_required
from google.appengine.api import users, memcache, search, mail
from google.appengine.ext import ndb, blobstore
from google.appengine.runtime import apiproxy_errors

from wtforms import widgets, fields
from models import INDEX, Photo, Entry, Cloud, Graph
from config import DEVEL, LANGUAGES, PER_PAGE, PHOTOS_PER_PAGE, ENTRIES_PER_PAGE, MAIL_BODY, FAMILY, TIMEOUT


def csrf_protected(handler_method):
    def wrapper(self, *args, **kwargs):
        token = self.request.params.get('token')
        if token and self.session.get('csrf') == token:
            if self.request.headers.get('X-Requested-With') is None:
                self.session['csrf'] = uuid.uuid1().hex
            handler_method(self, *args, **kwargs)
        else:
            self.abort(400)
    return wrapper


def xss_protected(handler_method):
    def wrapper(self, *args, **kwargs):
        for key, val in self.request.params.items():
            if key == 'page':
                try:
                    int(val)
                except ValueError:
                    self.abort(400)
            elif key == 'find':
                pass
            else:
                if val != Markup.escape(val):
                    self.abort(400)
        handler_method(self, *args, **kwargs)
    return wrapper


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, users.User):
            return obj.email()
        return obj


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        return self.session_store.get_session()

    @webapp2.cached_property
    def user(self):
        return users.get_current_user()

    @webapp2.cached_property
    def is_admin(self):
        return users.is_current_user_admin()

    @webapp2.cached_property
    def csrf_token(self):
        if self.session.get('csrf', None) is None:
            self.session['csrf'] = uuid.uuid1().hex
        return self.session.get('csrf')

    def handle_exception(self, exception, debug):
        template = 'error.html'
        if isinstance(exception, webapp2.HTTPException):
            data = {'error': exception, 'path': self.request.path_qs}
            self.render_template(template, data)
            self.response.set_status(exception.code)
        else:
            data = {'error': exception, 'lines': ''.join(traceback.format_exception(*sys.exc_info()))}
            if not DEVEL and not isinstance(exception, apiproxy_errors.OverQuotaError):
                mail.AdminEmailMessage(
                    sender='ANDS Outage <outage@andsnews.appspotmail.com>',
                    subject='Server Error traceback',
                    body=MAIL_BODY.format(**data)
                ).send()
            self.render_template(template, data)
            self.response.set_status(500)

    def render_template(self, filename, kwargs):
        # http://effbot.org/zone/default-values.htm
        lang_code = self.session.get('lang_code', 'en_US')
        i18n.get_i18n().set_locale(lang_code)

        if 'headers' in kwargs:
            self.response.headers = kwargs['headers']
            del kwargs['headers']

        kwargs.update({
            'language_code': lang_code,
            'user': self.user,
            'is_admin': self.is_admin,
            'token': self.csrf_token
        })
        self.response.headers['X-XSS-Protection'] = '1;mode=block'
        self.response.write(self.jinja2.render_template(filename, **kwargs))

    def render_json(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class Complete(BaseHandler):
    def get(self, mem_key):
        cloud = Cloud(mem_key).get_list()
        term = self.request.get('term', '').lower()
        data = [{'id': x['name'], 'value': x['name']} for x in cloud if term in x['name'].lower()]
        self.render_json(data)


class SetLanguage(BaseHandler):
    def post(self):
        next = self.request.headers.get('Referer', self.uri_for('start'))
        language = self.request.get('language')
        if language in dict(LANGUAGES):
            self.session['lang_code'] = language
        self.redirect(next)


class Sign(BaseHandler):
    def get(self):
        referer = self.request.headers.get('Referer', self.uri_for('start'))
        if referer.endswith('admin/'):
            referer = self.uri_for('start')
        if users.get_current_user():
            self.session.pop('csrf', None)
            dest_url = users.create_logout_url(referer)
            logging.info('LOGGED IN AS %s' % users.get_current_user().email())
        else:
            dest_url = users.create_login_url(referer)
        self.redirect(dest_url)


class Find(BaseHandler):
    @xss_protected
    def get(self):
        find = self.request.get('find').strip()
        page = int(self.request.get('page', 1))
        paginator = SearchPaginator(find, per_page=PER_PAGE)
        futures, number_found, has_next, error = paginator.page(page)

        self.render_template(
            'results.html', {
                'futures': futures, 'phrase': find, 'number_found': number_found,
                'page': page, 'has_next': has_next, 'has_previous': page > 1, 'error': error})


class DeleteHandler(BaseHandler):
    @login_required
    def get(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        next = self.request.headers.get('Referer', self.uri_for('start'))
        obj = key.get()
        if not any([self.is_admin, self.user == obj.author]):
            self.abort(403)
        data = {'object': obj, 'post_url': self.request.path, 'next': next}
        self.render_template('snippets/confirm.html', data)

    @csrf_protected
    def post(self, safe_key):
        next = str(self.request.get('next'))
        key = ndb.Key(urlsafe=safe_key)
        key.delete()
        self.redirect(next)


class SaveAsHandler(BaseHandler):
    @login_required
    def get(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        obj = key.get()
        blob_reader = blobstore.BlobReader(obj.blob_key, buffer_size=1024*1024)
        buff = blob_reader.read(size=-1)
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s.jpg' % key.string_id()
        logging.info('%s downloaded %s.jpg' % (self.user.nickname(), key.string_id()))
        self.response.write(buff)


class Paginator(object):
    timeout = TIMEOUT / 12  # 5 min

    def __init__(self, query, per_page=PER_PAGE):
        self.query = query
        self.per_page = per_page
        # <str> repr(self.query)
        self.id = hashlib.md5('{0}{1}'.format(self.query, self.per_page)).hexdigest()
        self.cache = memcache.get(self.id) or {}

    def page_keys(self, num):
        if num < 1:
            webapp2.abort(404)

        try:
            cursor = self.cache[num - 1]
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, start_cursor=cursor)
        except (KeyError, TypeError):
            offset = (num - 1) * self.per_page
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, offset=offset)

        self.cache[num] = cursor
        memcache.set(self.id, self.cache, self.timeout)
        return keys, has_next

    def page(self, num):
        keys, has_next = self.page_keys(num)
        objects = ndb.get_multi(keys)
        # get_multi returns a list whose items are either a Model instance or None if the key wasn't found.
        return [x for x in objects if x is not None], has_next


class SearchPaginator(object):
    timeout = TIMEOUT/12

    def __init__(self, querystring, per_page=PER_PAGE):
        self.querystring = querystring
        self.per_page = per_page

        self.options = {
            'cursor': search.Cursor(),
            'limit': self.per_page,
            'ids_only': True,
            'sort_options': search.SortOptions(
                expressions=[
                    search.SortExpression(
                        expression='year * 12 + month',
                        direction=search.SortExpression.DESCENDING, default_value=2030*12)
                ]
            )
        }
        self.id = hashlib.md5(querystring).hexdigest()
        self.cache = memcache.get(self.id) or {}

    def page(self, num):
        futures, has_next, number_found, error = [], False, 0, None

        if self.querystring:
            try:
                cursor = self.cache[num]
            except KeyError:
                cursor = None
            try:
                self.options['cursor'] = search.Cursor(web_safe_string=cursor)
                query = search.Query(
                    query_string=self.querystring,
                    options=search.QueryOptions(**self.options)
                )
                found = INDEX.search(query)
                results = found.results
            except search.Error as e:
                error = e.message
            else:
                number_found = found.number_found
                keys = [ndb.Key(urlsafe=doc.doc_id) for doc in results]
                futures = ndb.get_multi_async(keys)

                if found.cursor is not None:
                    has_next = True
                    self.cache[num + 1] = found.cursor.web_safe_string
                    memcache.set(self.id, self.cache, self.timeout)

        return futures, number_found, has_next, error


class RenderCloud(BaseHandler):
    def get(self, mem_key, value=None):
        kind, field = mem_key.split('_')
        items = Cloud(mem_key).get_list()

        if field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
            items = sorted(items, key=itemgetter('count'), reverse=True)

        if field == 'date':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        elif field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
            items = sorted(items, key=itemgetter('name'), reverse=False)
        elif field == 'color':
            items = sorted(items, key=itemgetter('order'))

        self.render_template(
            'snippets/cloud.html', {
                'items': items,
                'link': '%s_all_filter' % kind.lower(),
                'field_name': field,
                'filter': {'field': field, 'value': value} if (field and value) else None})


class RenderGraph(BaseHandler):
    def get(self, mem_key):
        kind, field = mem_key.split('_')
        items = Cloud(mem_key).get_list()

        if field in ('tags', 'author', 'model', 'lens', 'eqv', 'iso',):
            items = sorted(items, key=itemgetter('count'), reverse=True)

        if field == 'date':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        elif field in ('eqv', 'iso',):
            items = sorted(items, key=itemgetter('name'), reverse=False)
        elif field == 'color':
            items = sorted(items, key=itemgetter('order'))

        self.render_template('snippets/graph.html', {'items': items[:10], 'field_name': field})


class Plain(BaseHandler):
    def get(self):
        self.render_template('graph.html', {})


class DrawGraph(BaseHandler):
    def get(self, field):
        data = Graph(field).get_json()
        self.render_json(data)


class SiteMap(BaseHandler):
    def get(self):
        query = Photo.query().order(-Photo.date)
        paginator = Paginator(query, per_page=PHOTOS_PER_PAGE)
        photos, _ = paginator.page(1)

        query = Entry.query().order(-Entry.date)
        paginator = Paginator(query, per_page=ENTRIES_PER_PAGE)
        entries, _ = paginator.page(1)

        data = {'photos': photos,
                'entries': entries,
                'headers': [('Content-Type', 'application/xml')]}
        self.render_template('urlset.xml', data)


class EmailField(fields.SelectField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)
        user = users.get_current_user()
        email = user.email()
        if email not in FAMILY:
            FAMILY.append(email)
        self.choices = [(users.User(x).nickname(), x) for x in FAMILY]


class TagsField(fields.StringField):
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
