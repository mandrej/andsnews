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
from models import INDEX, Photo, Entry
from config import DEVEL


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
