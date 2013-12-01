from __future__ import division
import hashlib
from string import capitalize
import datetime

import webapp2
from google.appengine.api import users, memcache, xmpp
from google.appengine.ext import ndb

from wtforms import widgets, fields
from config import to_datetime, ADMIN_JID, CROPS, FAMILY, PER_PAGE, RSS_LIMIT, RFC822, TIMEOUT
from models import Photo, Entry, Comment
from handlers import BaseHandler
from models import Cloud


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


class Latest(BaseHandler):
    def get(self):
        objects = memcache.get('Photo_latest')
        if objects is None:
            query = Photo.query().order(-Photo.date)
            paginator = Paginator(query)
            results, has_next = paginator.page(1)
            objects = [x.normal_url() for x in results]
            memcache.add('Photo_latest', objects, TIMEOUT)
        self.render_json(objects)


class Index(BaseHandler):
    def get(self):
        self.render_template('index.html')


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
        else:
            try:
                cursor = self.cache[num - 1]['cursor']
                keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, start_cursor=cursor)
            except KeyError:
                offset = (num - 1) * self.per_page
                keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, offset=offset)

        if not keys:
            if num == 1:
                return keys, False
            else:
                webapp2.abort(404)

        if keys and cursor:
            self.cache[num] = {'cursor': cursor, 'keys': keys, 'has_next': has_next}
            memcache.replace(self.id, self.cache, self.timeout)
            return keys, has_next
        else:
            webapp2.abort(404)

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


class Chat(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        message.reply("ANDS thank you!")

        email = message.sender.split('/')[0]  # node@domain/resource
        user = users.User(email)
        obj = Comment(author=user, body=message.body)
        obj.add()


class Send(webapp2.RequestHandler):
    def post(self):
        message = self.request.get('msg')
        xmpp.send_message(ADMIN_JID, message)


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