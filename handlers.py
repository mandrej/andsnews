from __future__ import division

__author__ = 'milan'

import json
import datetime
import sys
import traceback
import hashlib
import uuid
import webapp2
from operator import itemgetter
from jinja2.filters import do_striptags
from string import capitalize
from wtforms import widgets, fields
from webapp2_extras import i18n, sessions, jinja2
from webapp2_extras.appengine.users import login_required
from google.appengine.api import users, search, memcache, xmpp
from google.appengine.ext import ndb
from models import Photo, Entry, Comment, Cloud, INDEX
from config import to_datetime, RESULTS, PER_PAGE, RSS_LIMIT, CROPS, FAMILY, TIMEOUT, RFC822, OFFLINE, DEVEL


def touch_appcache(handler_method):
    def wrapper(self, *args, **kwargs):
        memcache.replace('appcache', OFFLINE % datetime.datetime.now().isoformat())
        handler_method(self, *args, **kwargs)
    return wrapper


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


def auto_complete(request, mem_key):
    response = webapp2.Response(content_type='text/plain')
    if mem_key == 'Photo_crop_factor':
        mem_key = 'Photo_model'
        cloud = Cloud(mem_key).get_list()
        factors = list(set([CROPS[x.get('name')] for x in cloud]))
        factors.sort()
        words = map(str, factors)
    else:
        cloud = Cloud(mem_key).get_list()
        words = [x['name'] for x in cloud]
        words.sort()

    response.write('\n'.join(words))
    return response


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
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
        if self.session.get('csrf', None) is None:
            self.session['csrf'] = uuid.uuid1().hex
        return self.session.get('csrf')

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

    def render_template(self, filename, kwargs={}):
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
        kwargs['caching'] = not DEVEL and kwargs.get('form', None) is None
        self.response.write(self.jinja2.render_template(filename, **kwargs))

    def render_json(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class Latest(BaseHandler):
    def get(self):
        objects = memcache.get('Photo_latest')
        if objects is None:
            query = Photo.query().order(-Photo.date)
            paginator = Paginator(query, per_page=15)
            results, has_next = paginator.page(1)
            objects = [x.normal_url for x in results]
            memcache.add('Photo_latest', objects, TIMEOUT)
            memcache.add('appcache', OFFLINE % datetime.datetime.now().isoformat())
        self.render_json(objects)


class Index(BaseHandler):
    def get(self):
        self.render_template('index.html')


class SetLanguage(BaseHandler):
    @touch_appcache
    def post(self):
        next = self.request.headers.get('Referer', webapp2.uri_for('start'))
        self.session['lang_code'] = self.request.get('language')
        self.redirect(next)


class Sign(BaseHandler):
    @touch_appcache
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


class AppCache(webapp2.RequestHandler):
    def get(self):
        appcache = memcache.get('appcache')
        if appcache is None:
            memcache.add('appcache', OFFLINE % datetime.datetime.now().isoformat())
        self.response.headers['Content-Type'] = 'text/cache-manifest'
        self.response.write(appcache)


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
    @touch_appcache
    def post(self, safe_key):
        next = str(self.request.get('next'))
        key = ndb.Key(urlsafe=safe_key)
        key.delete()
        self.redirect(next)


class Filter(object):
    def __init__(self, field, value):
        self.field, self.value = field, value

    @webapp2.cached_property
    def parameters(self):
        try:
            assert (self.field and self.value)
        except AssertionError:
            return {}
        else:
            if self.field == 'date':
                return {'year': int(self.value)}
            elif self.field == 'author':
                # TODO Not all emails are gmail
                return {self.field: users.User(email='%s@gmail.com' % self.value)}
            elif self.field == 'forkind':
                return {self.field: capitalize(self.value)}
            elif self.field == 'hue':
                return {self.field: self.value, 'sat': 'color'}
            elif self.field == 'lum':
                return {self.field: self.value, 'sat': 'monochrome'}
            else:
                try:
                    self.value = int(self.value)
                except ValueError:
                    pass
                return {'%s' % self.field: self.value}


class Paginator(object):
    timeout = TIMEOUT / 6

    def __init__(self, query, per_page=PER_PAGE):
        self.query = query
        self.per_page = per_page
        self.id = hashlib.md5(repr(self.query)).hexdigest()
        self.cache = memcache.get(self.id)

        if self.cache is None:
            self.cache = {0: {'cursor': None, 'keys': [], 'has_next': True}}
            memcache.add(self.id, self.cache, self.timeout)

    def page_keys(self, num):
        if num < 1:
            webapp2.abort(404)

        if num in self.cache and self.cache[num]['keys']:
            return self.cache[num]['keys'], self.cache[num]['has_next']

        try:
            cursor = self.cache[num - 1]['cursor']
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, start_cursor=cursor)
        except KeyError:
            offset = (num - 1) * self.per_page
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, offset=offset)

        if not keys and num == 1:
            return keys, has_next

        self.cache[num] = {'cursor': cursor, 'keys': keys, 'has_next': has_next}
        memcache.replace(self.id, self.cache, self.timeout)
        return keys, has_next

    def page(self, num):
        keys, has_next = self.page_keys(num)
        return ndb.get_multi(keys), has_next

    def triple(self, slug, idx):
        """ num and idx are 1 base index """
        none = ndb.Key('XXX', 'xxx')
        rem = idx % self.per_page
        num = int(idx / self.per_page) + (0 if rem == 0 else 1)
        keys, has_next = self.page_keys(num)

        if rem == 1:
            if num == 1:
                collection = [none] + keys + [none]
            else:
                other, x = self.page_keys(num - 1)
                collection = (other + keys + [none])[idx - (num - 2) * self.per_page - 2:]
        else:
            if has_next:
                other, x = self.page_keys(num + 1)
            else:
                other = [none]
            collection = (keys + other)[idx - (num - 1) * self.per_page - 2:]

        try:
            prev, obj, next = ndb.get_multi(collection[:3])
        except ValueError:
            webapp2.abort(404)
        else:
            return num, prev, obj, next


class SearchPaginator(object):
#    timeout = 60 #TIMEOUT/10
    def __init__(self, querystring, per_page=PER_PAGE):
        self.querystring = querystring
        # '"{0}"'.format(querystring.replace('"', ''))
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
        # opts = {
        #     'limit': self.per_page,
        #     'returned_fields': ['headline', 'author', 'tags', 'date', 'link', 'kind'],
        #     'returned_expressions': [
        #         search.FieldExpression(name='body', expression='snippet("%s", body)' % self.querystring)
        #     ],
        #     'snippeted_fields': ['body']
        # }
        # try:
        #     cursor = self.cache[num]
        # except KeyError:
        #     cursor = None
        #
        # opts['cursor'] = search.Cursor(web_safe_string=cursor)
        # opts['offset'] = (num - 1)*self.per_page
        # found = INDEX.search(search.Query(query_string=self.querystring,
        #                                   options=search.QueryOptions(**opts)))
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
        except search.Error, error:
            pass
        except UnicodeDecodeError, error:
            pass
        else:
            if number_found > 0:
                has_next = number_found > num * self.per_page
                # self.cache[num + 1] = found.cursor.web_safe_string
                # memcache.replace(self.id, self.cache, self.timeout)

        return results, number_found, has_next, error


class Chat(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        message.reply("ANDS thank you!")

        email = message.sender.split('/')[0]  # node@domain/resource
        user = users.User(email)
        obj = Comment(author=user, body=message.body)
        obj.add()


#class Send(webapp2.RequestHandler):
#    def post(self):
#        message = self.request.get('msg')
#        xmpp.send_message(ADMIN_JID, message)


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


class Rss(BaseHandler):
    def get(self, kind):
        if kind == 'photo':
            query = Photo.query().order(-Photo.date)
        elif kind == 'entry':
            query = Entry.query().order(-Entry.date)

        data = {'kind': kind,
                'objects': query.fetch(RSS_LIMIT),
                'format': RFC822}

        last_modified = to_datetime(data['objects'][0].date, format=RFC822)
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        data['headers'] = [('Content-Type', 'application/rss+xml'),
                           ('Last-Modified', last_modified),
                           ('ETag', hashlib.md5(last_modified).hexdigest()),
                           ('Expires', to_datetime(expires, format=RFC822)),
                           ('Cache-Control', 'max-age=86400')]
        self.render_template('rss.xml', data)


class SiteMap(BaseHandler):
    def get(self):
        data = {'photos': Photo.query().order(-Photo.date),
                'entries': Entry.query().order(-Entry.date),
                'headers': [('Content-Type', 'application/xml')]}
        self.render_template('urlset.xml', data)


class PhotoMeta(BaseHandler):
    def get(self):
        fields = ('author', 'tags', 'size', 'model', 'aperture', 'shutter',
                  'focal_length', 'iso', 'date', 'lens', 'crop_factor', 'eqv', 'color',)
        data = []
        for x in Photo.query().order(-Photo.date):
            row = x.to_dict(include=fields)
            row['slug'] = x.key.string_id()
            data.append(row)
        self.render_json(data)


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