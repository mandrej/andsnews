__author__ = 'milan'

import json
import datetime
import sys
import traceback
import uuid
from operator import itemgetter

import webapp2
from webapp2_extras import i18n, sessions, jinja2
from webapp2_extras.appengine.users import login_required
from jinja2.filters import do_striptags
from google.appengine.api import users
from google.appengine.ext import ndb
from common import SearchPaginator
from models import Cloud
from config import DEVEL, RESULTS, LANGUAGES


def csrf_protected(handler):
    def inner(self, *args, **kwargs):
        token = self.request.params.get('token')
        if token and self.session.get('csrf') == token:
            handler(self, *args, **kwargs)
        else:
            self.abort(400)
    return inner


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, users.User):
            return obj.email()
        return obj


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
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
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def user(self):
        return users.get_current_user()

    @webapp2.cached_property
    def is_admin(self):
        return users.is_current_user_admin()

    @webapp2.cached_property
    def csrf_token(self):
        if self.user and self.session.get('csrf', None) is None:
            self.session['csrf'] = uuid.uuid1().hex
        return self.session.get('csrf', None)

    def handle_exception(self, exception, debug):
        template = 'errors/default.html'
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

        values = {
            'LANGUAGE_CODE': lang_code,
            'LANGUAGES': LANGUAGES,
            'user': self.user,
            'is_admin': self.is_admin,
            'token': self.csrf_token,
            'devel': DEVEL
        }
        if 'headers' in kwargs:
            self.response.headers = kwargs['headers']
            del kwargs['headers']

        kwargs.update(values)
        self.response.write(self.jinja2.render_template(filename, **kwargs))

    def render_json(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        self.response.write(json.dumps(data, cls=LazyEncoder))


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
        if not self.is_admin:
            if self.user != obj.author:
                self.abort(403)
        data = {'object': obj, 'post_url': self.request.path, 'next': next}
        self.render_template('snippets/confirm.html', data)

    @csrf_protected
    def post(self, safe_key):
        next = str(self.request.get('next'))
        key = ndb.Key(urlsafe=safe_key)
        key.delete()
        self.redirect(next)


class SetLanguage(BaseHandler):
    def post(self):
        next = self.request.headers.get('Referer', webapp2.uri_for('start'))
        self.session['lang_code'] = self.request.get('language')
        self.redirect(next)


class Sign(BaseHandler):
    def get(self):
        referer = self.request.headers.get('Referer', webapp2.uri_for('start'))
        if referer.endswith('admin/'):
            referer = webapp2.uri_for('start')
        if users.get_current_user():
            self.session.pop('csrf', None)
            dest_url = users.create_logout_url(referer)
        else:
            dest_url = users.create_login_url(referer)
        self.redirect(dest_url)