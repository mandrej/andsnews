# -*- coding: UTF-8 -*-
from __future__ import division
import os, json, webapp2, jinja2
from webapp2_extras import i18n, sessions
import hashlib, datetime
from gettext import gettext as _
from operator import itemgetter
from google.appengine.ext import ndb
from google.appengine.api import users, memcache, xmpp
from models import Photo, Entry, Comment
from common import ENV, BaseHandler, Filter, SearchPaginator, make_cloud, count_colors
from settings import TIMEOUT, ADMIN_JID
import sys, logging, traceback

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

#TODO if self.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
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
        querystring = self.request.GET.get('find')
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
        objects = [{"url": x.normal_url(),
                    "date": x.date.strftime('%Y-%m-%d'),
                    "title": x.headline} for x in query.iter(limit=NUM_LATEST)]
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
#    @login_required
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
    template = ENV.get_template('403.html')
    response.out.write(template.render({'error': exception}))
    response.set_status(403)
    return response

def handle_404(request, response, exception):
    template = ENV.get_template('404.html')
    response.out.write(template.render({'error': exception, 'path': request.path_qs}))
    response.set_status(404)
    return response

def handle_500(request, response, exception):
    template = ENV.get_template('500.html')
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

def rfc822_date(dt):
    return dt.strftime('%a, %d %b %Y %I:%M:%S %p GMT')

def rss(request, kind):
    if kind == 'photo':
        query = Photo.query().order(-Photo.date)
        data = query.fetch(RSS_LIMIT)
        last_modified = rfc822_date(data[0].date)
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        str = u'<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel>'
        str += u'<title>АNDрејевићи photo album</title>'
        str += u'<link>http://%s/photos</link>' % HOST_NAME
        str += u'<lastBuildDate>%s</lastBuildDate>' % last_modified
        str += u'<description>Latest photos from the site</description>'

        for item in data:
            str += u'<item><title>%s</title>' % escape(item.headline)
            text = u'Camera model: %s' % escape(item.model)
            if item.lens: text += u', Lens type: %s' % escape(item.lens)
            if item.aperture: text += u', Aperture: F%s' % item.aperture
            if item.shutter: text += u', Shutter speed: %s sec' % item.shutter
            if item.focal_length: text += u', Focal length: %s mm (~ %s eqv.)' % (item.focal_length, item.eqv)
            if item.iso: text += u', Sensitivity (ISO): %s ASA' % item.iso
            str += u'<description>%s</description>' % text
#            TODO small
#            str += u'<enclosure url="http://%s%s/small" length="%s" type="image/jpeg"></enclosure>' % (HOST_NAME, item.get_absolute_url(), len(item.picture.get().small))
            str += u'<link>http://%s%s</link>' % (HOST_NAME, item.get_absolute_url())
            str += u'<author>%s</author>' % item.author.email()
            str += u'<pubDate>%s</pubDate>' % rfc822_date(item.date)
            str += u'<guid isPermaLink="true">http://%s%s</guid>' % (HOST_NAME, item.get_absolute_url())
            text = ','.join(item.tags)
            str += u'<category>%s</category>' % escape(text)
            str += u'</item>'
        str += u'</channel></rss>'
    elif kind == 'entry':
        query = Entry.query().order(-Entry.date)
        data = query.fetch(RSS_LIMIT)
        last_modified = rfc822_date(data[0].date)
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        str = u'<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel>'
        str += u'<title>АNDрејевићи blog</title>'
        str += u'<link>http://%s/entries</link>' % HOST_NAME
        str += u'<lastBuildDate>%s</lastBuildDate>' % last_modified
        str += u'<description>Latest blog entries from the site</description>'

        for item in data:
            str += u'<item><title>%s</title>' % escape(item.headline)
            str += u'<description>%s</description>' % escape(item.summary)
            str += u'<link>http://%s%s</link>' % (HOST_NAME, item.get_absolute_url())
            str += u'<author>%s</author>' % item.author.email()
            str += u'<pubDate>%s</pubDate>' % rfc822_date(item.date)
            str += u'<guid isPermaLink="true">http://%s%s</guid>' % (HOST_NAME, item.get_absolute_url())
            text = ','.join(item.tags)
            str += u'<category>%s</category>' % escape(text)
            str += u'</item>'
        str += u'</channel></rss>'

    response = webapp2.Response(content_type='application/rss+xml')
    response.headers['Last-Modified'] = last_modified
    response.headers['ETag'] = hashlib.md5(last_modified).hexdigest()
    response.headers['Expires'] = rfc822_date(expires)
    response.headers['Cache-Control'] = 'max-age=86400'
    response.out.write(str)
    return response

def sitemap(request):
    logging.error(type(request))
    out = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    head = '<url><loc>%s</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>'
    row = '<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.3</priority></url>'
    loc = 'http://%s%s' % (HOST_NAME, '/photos')
    out += head % loc
    for item in Photo.query().order(-Photo.date):
        loc = 'http://%s%s' % (HOST_NAME, item.get_absolute_url())
    out += row % (loc, item.date.date())
    loc = 'http://%s%s' % (HOST_NAME, '/entries')
    out += head % loc

    for item in Entry.query().order(-Entry.date):
        loc = 'http://%s%s' % (HOST_NAME, item.get_absolute_url())
    out += row % (loc, item.date.date())
    out += '</urlset>'
    response = webapp2.Response(content_type='application/xml')
    response.out.write(out)
    return response