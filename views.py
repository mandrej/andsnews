from __future__ import division
import hashlib
import datetime

import webapp2
from google.appengine.api import users, memcache, xmpp

from models import Photo, Entry, Comment
from handlers import BaseHandler
from config import to_datetime, ADMIN_JID, TIMEOUT, CROPS
from models import Cloud

RSS_LIMIT = 10
NUM_LATEST = 6
RFC822 = '%a, %d %b %Y %I:%M:%S %p GMT'


def auto_complete(request, mem_key):
    response = webapp2.Response(content_type='text/plain')
    if mem_key == 'Photo_crop_factor':
        mem_key = 'Photo_model'
        cloud = Cloud(mem_key).get_list()
        words = [str(CROPS[x['name']]) for x in cloud]
    else:
        cloud = Cloud(mem_key).get_list()
        words = [x['name'] for x in cloud]

    words.sort()
    response.write('\n'.join(words))
    return response


def get_latest_photos():
    objects = memcache.get('Photo_latest')
    if objects is None:
        query = Photo.query().order(-Photo.date)
        results, cursor, has_next = query.fetch_page(NUM_LATEST)
        objects = [{"url": x.normal_url(),
                    "title": x.headline} for x in results]
        memcache.add('Photo_latest', objects, TIMEOUT)
    return objects


class Latest(BaseHandler):
    def get(self):
        self.render_json(get_latest_photos())


class Index(BaseHandler):
    def get(self):
        objects = get_latest_photos()
        self.render_template('index.html', {'latest': objects})


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