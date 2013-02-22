from __future__ import division
import os
import json
import hashlib
import datetime
from operator import itemgetter

import webapp2
from jinja2.filters import do_striptags
from google.appengine.ext import ndb
from google.appengine.api import users, memcache, xmpp

from models import Photo, Entry, Comment
from common import ENV, BaseHandler, SearchPaginator, make_cloud, count_colors, format_datetime
from settings import TIMEOUT, ADMIN_JID, RFC822


RESULTS = 12
RSS_LIMIT = 10
NUM_LATEST = 6

PORT = os.environ['SERVER_PORT']
if PORT and PORT != '80':
    HOST_NAME = '%s:%s' % (os.environ['SERVER_NAME'], PORT)
else:
    HOST_NAME = os.environ['SERVER_NAME']


def get_or_build(key):
    kind, field = key.split('_')
    items = memcache.get(key)
    if items is None:
        if field == 'colors':
            items = count_colors()
        else:
            items = make_cloud(kind, field)

    if field != 'colors':
        # 10 most frequent
        items = sorted(items, key=itemgetter('count'), reverse=True)[:10]
    return items


class RenderCloud(BaseHandler):
    def get(self, key, value=None):
        kind, field = key.split('_')
        items = get_or_build(key)
        self.render_template(
            'snippets/x_%s.html' % field, {
                'items': items,
                'link': '%s_filter_all' % kind.lower(),
                'filter': {'field': field, 'value': value} if (field and value) else None})


class RenderGraph(BaseHandler):
    def get(self, key):
        kind, field = key.split('_')
        items = get_or_build(key)
        if field == 'date':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        elif field in ('eqv', 'iso'):
            items = sorted(items, key=itemgetter('name'), reverse=False)

        self.render_template('snippets/x_%s.html' % field, {'items': items, 'graph': True})


def auto_complete(request, kind, field):
    words = [x['name'] for x in make_cloud(kind.capitalize(), field)]
    words.sort()
    response = webapp2.Response(content_type='text/plain')
    response.write('\n'.join(words))
    return response


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
                link = webapp2.uri_for(key.kind().lower(), slug=key.string_id())

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


def get_latest_photos():
    objects = memcache.get('Photo_latest')
    if objects is None:
        query = Photo.query().order(-Photo.date)
        results, cursor, has_next = query.fetch_page(NUM_LATEST)
        objects = [{"url": x.normal_url(),
                    "title": x.headline} for x in results]
        memcache.add('Photo_latest', objects, TIMEOUT)
    return objects


def latest(request):
    objects = get_latest_photos()
    response = webapp2.Response(content_type='application/json')
    response.write(json.dumps(objects))
    return response


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


def rss(request, kind):
    template = ENV.get_template('rss.xml')
    if kind == 'photo':
        query = Photo.query().order(-Photo.date)
        data = {'title': 'Photos',
                'link': webapp2.uri_for('photo_all'),
                'description': 'Latest photos from the site'}
    elif kind == 'entry':
        query = Entry.query().order(-Entry.date)
        data = {'title': 'Entries',
                'link': webapp2.uri_for('entry_all'),
                'description': 'Latest entries from the site'}

    data.update({'kind': kind,
                 'HOST': 'http://%s' % HOST_NAME,
                 'objects': query.fetch(RSS_LIMIT),
                 'format': RFC822})
    last_modified = format_datetime(data['objects'][0].date, format=RFC822)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    response = webapp2.Response(content_type='application/rss+xml')
    response.headers['Last-Modified'] = last_modified
    response.headers['ETag'] = hashlib.md5(last_modified).hexdigest()
    response.headers['Expires'] = format_datetime(expires, format=RFC822)
    response.headers['Cache-Control'] = 'max-age=86400'
    response.write(template.render(data))
    return response


def sitemap(request):
    template = ENV.get_template('urlset.xml')
    data = {'photos': Photo.query().order(-Photo.date),
            'entries': Entry.query().order(-Entry.date),
            'HOST': 'http://%s' % HOST_NAME}
    response = webapp2.Response(content_type='application/xml')
    response.write(template.render(data))
    return response