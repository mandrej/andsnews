from __future__ import division

import json
import datetime
import uuid
import logging
from operator import itemgetter

import webapp2
from jinja2.filters import Markup
from webapp2_extras import i18n, sessions, jinja2
from google.appengine.api import users, search, mail, datastore_errors
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

from models import INDEX, Photo, Entry
from config import DEVEL, PER_PAGE, PHOTOS_PER_PAGE, ENTRIES_PER_PAGE, FAMILY


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
            if key == 'find':
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

    def render_template(self, filename, kwargs):
        lang_code = self.session.get('lang_code', 'en_US')
        self.session['lang_code'] = lang_code
        i18n.get_i18n().set_locale(lang_code)

        if self.session.get('csrf', None) is None:
            self.session['csrf'] = uuid.uuid1().hex

        if 'headers' in kwargs:
            self.response.headers = kwargs['headers']
            del kwargs['headers']

        kwargs.update({
            'user': self.user,
            'is_admin': self.is_admin,
            'session': self.session
        })
        self.response.headers['X-XSS-Protection'] = '1;mode=block'
        self.response.write(self.jinja2.render_template(filename, **kwargs))

    def render_json(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class Sign(BaseHandler):
    def get(self):
        referrer = '/' # self.request.headers.get('Referer', self.uri_for('start'))
        if users.get_current_user():
            self.session.pop('csrf', None)
            if referrer.endswith('admin/'):
                referrer = '/'  # self.uri_for('start')
            url = users.create_logout_url(referrer)
        else:
            url = users.create_login_url(referrer)
        self.redirect(url)


class Paginator(object):
    def __init__(self, query, per_page=PER_PAGE):
        self.query = query
        self.per_page = per_page

    def page(self, token=None):
        try:
            cursor = Cursor(urlsafe=token)
        except datastore_errors.BadValueError:
            webapp2.abort(404)

        objects, cursor, has_next = self.query.fetch_page(self.per_page, start_cursor=cursor)
        next_token = cursor.urlsafe() if has_next else None
        return [x for x in objects if x is not None], next_token


class SearchPaginator(object):
    def __init__(self, querystring, per_page=PER_PAGE):
        self.querystring = querystring
        self.per_page = per_page

        self.options = {
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

    def page(self, token=None):
        objects, next_token, number_found, error = [], None, 0, None
        if token is not None:
            self.options['cursor'] = search.Cursor(web_safe_string=token)
        else:
            self.options['cursor'] = search.Cursor()

        if self.querystring:
            try:
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
                objects = ndb.get_multi(keys)

                if found.cursor is not None:
                    next_token = found.cursor.web_safe_string

        return [x for x in objects if x is not None], number_found, next_token, error


def cloud_limit(items):
    """
    Returns limit for the specific count. Show only if count > limit
    :param items: dict {Photo_tags: 10, _date: 119, _eqv: 140, _iso: 94, _author: 66, _lens: 23, _model: 18, _color: 73
    :return: int
    """
    if DEVEL:
        return 0
    else:
        _curr = 0
        _sum5 = sum((x['count'] for x in items)) * 0.05
        if _sum5 < 1:
            return 0
        else:
            _on_count = sorted(items, key=itemgetter('count'))
            for item in _on_count:
                _curr += item['count']
                if _curr >= _sum5:
                    return item['count']


class SiteMap(BaseHandler):
    def get(self):
        query = Photo.query().order(-Photo.date)
        paginator = Paginator(query, per_page=PHOTOS_PER_PAGE)
        photos, _ = paginator.page()

        query = Entry.query().order(-Entry.date)
        paginator = Paginator(query, per_page=ENTRIES_PER_PAGE)
        entries, _ = paginator.page()

        data = {'photos': photos,
                'entries': entries,
                'headers': [('Content-Type', 'application/xml')]}
        self.render_template('urlset.xml', data)
