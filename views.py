from __future__ import division
import sys, traceback, urllib
import os, json, webapp2
import hashlib, datetime
from webapp2_extras.appengine.users import login_required
from gettext import gettext as _
from operator import itemgetter
from google.appengine.ext import ndb
from google.appengine.api import users, memcache, xmpp
from models import Photo, Entry, Comment
from common import ENV, BaseHandler, Filter, SearchPaginator, make_cloud, count_colors, format_datetime
from settings import TIMEOUT, ADMIN_JID, RFC822
import logging

MAP = {'Photo': 'photos', 'Entry': 'entries', 'Comment': 'comments', 'Feed': 'news'}
RESULTS = 5
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
    return items

class RenderCloud(BaseHandler):
    def get(self, key, value=None):
        kind, field = key.split('_')
        items = get_or_build(key)
        f = Filter(field, value)
        self.render_template('snippets/%s_cloud.html' % field,
            {'%scloud' % field: items, 'kind': kind, 'link': '/%s/%s' % (MAP[kind], field), 'filter': f.parameters})

def visualize(request, key):
    data = {}
    items = get_or_build(key)
    if key in ['Photo_tags', 'Entry_tags', 'Feed_tags']:
        data['title'] = _('Tags')
    elif key in ['Photo_author', 'Entry_author', 'Comment_author']:
        data['title'] = _('Authors')
    elif key in ['Photo_date', 'Entry_date', 'Comment_date']:
        data['title'] = _('Dates')
        tmp = [{'name': str(x['name']), 'count': x['count']} for x in items]
        data['rows'] = sorted(tmp, key=itemgetter('name'), reverse=True)[:10]
    elif key == 'Photo_model':
        data['title'] = _('Camera model')
    elif key == 'Photo_lens':
        data['title'] = _('Lens type')
    elif key == 'Photo_eqv':
        data['title'] = _('Eqv. focal length')
        data['info'] = _('Equivalent focal lengths are calculated for a full format sensor or 35 mm film camera, rounded to nearset 10')
        tmp = [{'name': '%s mm %s.' % (x['name'], _('eqv')), 'count': x['count']} for x in items]
        data['rows'] = sorted(tmp, key=itemgetter('count'), reverse=True)[:10]
    elif key == 'Photo_iso':
        data['title']= '%s (ISO)' % _('Sensitivity')
        tmp = [{'name': '%s ASA' % x['name'], 'count': x['count']} for x in items]
        data['rows'] = sorted(tmp, key=itemgetter('count'), reverse=True)[:10]
    elif key == 'Photo_colors':
        data['title'] = _('Median color')
        data['info'] = _('Based od HLS color model')
        data['rows'] = [{'name': _(x['name']), 'count': x['count']} for x in items]
        data['colors'] = [x['hex'] for x in items]
    elif key == 'Comment_forkind':
        data['title'] = _('comments and messages').capitalize()

    if not 'rows' in data:
        data['rows'] = sorted(items, key=itemgetter('count'), reverse=True)[:10]

    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps(data))
    return response

def auto_complete(request, kind, field):
    words = [x['name'] for x in make_cloud(kind.capitalize(), field)]
    words.sort()
    response = webapp2.Response(content_type='text/plain')
    response.out.write('\n'.join(words))
    return response

class Find(BaseHandler):
    def get(self):
        querystring = self.request.GET['find']
        page = int(self.request.GET.get('page', 1))
        paginator = SearchPaginator(querystring, per_page=RESULTS)
        results, number_found, has_next = paginator.page(page)

        objects = []
        for doc in results:
            f = {}
            for field in doc.fields:
                f[field.name] = field.value
            for expr in doc.expressions:
                f[expr.name] = expr.value
            objects.append(f)

        self.render_template('results.html',
            {'objects': objects, 'phrase': querystring, 'number_found': number_found,
             'page': page, 'has_next': has_next, 'has_previous': page > 1})

def get_latest_photos():
    objects = memcache.get('Photo_latest')
    if objects is None:
        query = Photo.query().order(-Photo.date)
        results, cursor, has_next = query.fetch_page(NUM_LATEST)
        objects = [{"url": x.normal_url(),
                    "date": x.date.strftime('%Y-%m-%d'),
                    "title": x.headline} for x in results]
        memcache.add('Photo_latest', objects, TIMEOUT)
    return objects

def latest(request):
    objects = get_latest_photos()
    response = webapp2.Response(content_type='application/json')
    response.out.write(json.dumps(objects))
    return response

class Index(BaseHandler):
    def get(self):
        objects = get_latest_photos()
        self.render_template('index.html', {'latest': objects})

class DeleteHandler(BaseHandler):
    @login_required
    def get(self, safekey):
        key = ndb.Key(urlsafe=safekey)
        if key.parent():
            next = self.request.headers.get('Referer', '/')
        else:
            next = '/%s' % MAP[key.kind()]

        obj = key.get()
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                webapp2.abort(403)
        data = {'object': obj, 'post_url': self.request.path, 'next': next}
        self.render_template('snippets/confirm.html', data)

    def post(self, safekey):
        next = str(self.request.POST['next'])
        obj = ndb.Key(urlsafe=safekey).get()
        obj.delete()
        self.redirect(next)

def handle_403(request, response, exception):
    template = ENV.get_template('errors/403.html')
    response.out.write(template.render({'error': exception}))
    response.set_status(403)
    return response

def handle_404(request, response, exception):
    template = ENV.get_template('errors/404.html')
    response.out.write(template.render({'error': exception, 'path': request.path_qs}))
    response.set_status(404)
    return response

def handle_500(request, response, exception):
    template = ENV.get_template('errors/500.html')
    lines = ''.join(traceback.format_exception(*sys.exc_info()))
    response.out.write(template.render({'error': exception, 'lines': lines}))
    response.set_status(500)
    return response

class Chat(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        message.reply("ANDS thank you!")

        email = message.sender.split('/')[0] # node@domain/resource
        user = users.User(email)
        obj = Comment(author=user, body=message.body)
        obj.add()

class Send(webapp2.RequestHandler):
    def post(self):
        message = self.request.POST.get('msg')
        xmpp.send_message(ADMIN_JID, message)

def escape(str):
    return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def rss(request, kind):
    template = ENV.get_template('rss.xml')
    if kind == 'photo':
        query = Photo.query().order(-Photo.date)
        data = {
            'title': 'Photos',
            'link': '/photos',
            'description': 'Latest photos from the site'
        }
    elif kind == 'entry':
        query = Entry.query().order(-Entry.date)
        data = {
            'title': 'Entries',
            'link': '/entries',
            'description': 'Latest entries from the site'
            }
    data.update({
        'kind': kind,
        'HOST': 'http://%s' % HOST_NAME,
        'objects': query.fetch(RSS_LIMIT),
        'format': RFC822
    })
    last_modified = format_datetime(data['objects'][0].date, format=RFC822)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    response = webapp2.Response(content_type='application/rss+xml')
    response.headers['Last-Modified'] = last_modified
    response.headers['ETag'] = hashlib.md5(last_modified).hexdigest()
    response.headers['Expires'] = format_datetime(expires, format=RFC822)
    response.headers['Cache-Control'] = 'max-age=86400'
    response.out.write(template.render(data))
    return response

def sitemap(request):
    template = ENV.get_template('urlset.xml')
    data = {
        'photos': Photo.query().order(-Photo.date),
        'entries': Entry.query().order(-Entry.date),
        'HOST': 'http://%s' % HOST_NAME,
    }
    response = webapp2.Response(content_type='application/xml')
    response.out.write(template.render(data))
    return response