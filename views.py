# -*- coding: UTF-8 -*-
from __future__ import division
import hashlib, datetime
from operator import itemgetter
from google.appengine.api import users, memcache, xmpp
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.vary import vary_on_headers
from django.shortcuts import render
from models import Photo, Entry, Comment
from lib.comm import SearchPaginator, Filter, json_response, make_cloud, count_colors
from django.conf import settings

MAP = {'Photo': 'photos', 'Entry': 'entries', 'Comment': 'comments', 'Feed': 'news'}
RESULTS = 5
RSS_LIMIT = 10
NUM_LATEST = 6

def get_or_build(key):
    kind, field = key.split('_')
    items = memcache.get(key)
    if items is None:
        if field == 'colors':
            items = count_colors()
        else:
            items = make_cloud(kind, field)
    return items

def render_cloud(request, key, value=None):
    if request.is_ajax():
        kind, field = key.split('_')
        items = get_or_build(key)
        f = Filter(field, value)
        return render(request, 'snippets/%s_cloud.html' % field,
            {'%scloud' % field: items, 'kind': kind, 'link': '/%s/%s' % (MAP[kind], field), 'filter': f.parameters})

def visualize(request, key):
    if request.is_ajax():
        items = get_or_build(key)
        data = {}
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
                
    return json_response(data)

def auto_complete(request, kind, field):
    response = HttpResponse(mimetype='text/plain')
    if request.is_ajax():
        words = [x['name'] for x in make_cloud(kind.capitalize(), field)]
        words.sort()
        response.write('\n'.join(words))
    return response

def find(request, tmpl='results.html'):
    querystring = request.GET.get('find')
    page = int(request.GET.get('page', 1))
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
    
    return render(request, tmpl, {'objects': objects, 'phrase': querystring, 'number_found': number_found, 
                                  'page': page, 'has_next': has_next, 'has_previous': page > 1})

def get_latest_photos():
    objects = memcache.get('Photo_latest')
    if objects is None:
        query = Photo.query().order(-Photo.date)
        objects = [{"url": x.get_absolute_url(),
                    "date": x.date.strftime('%Y-%m-%d'),
                    "title": x.headline} for x in query.iter(limit=NUM_LATEST)]
        memcache.add('Photo_latest', objects, settings.TIMEOUT)
    return objects

def latest(request):
    if request.is_ajax():
        objects = get_latest_photos()
        return json_response(objects)

def index(request, tmpl='index.html'):
    objects = get_latest_photos()
    return render(request, tmpl, {'latest': objects})

def chat(request):
    if request.method == 'POST':
        message = xmpp.Message(request.POST)
        message.reply("ANDS thank you!")

        email = message.sender.split('/')[0] # node@domain/resource
        user = users.User(email)
        obj = Comment(author=user, body=message.body)
        obj.add()
        return HttpResponse(status=200)

def send(request):
    # used for Server error (500)
    if request.method == 'POST':
        message = request.POST.get('msg')
        xmpp.send_message(settings.ADMIN_JID, message)
        return HttpResponse(status=200)

def escape(str):
    return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def rfc822_date(dt):
    return dt.strftime('%a, %d %b %Y %I:%M:%S %p GMT')

@vary_on_headers('Host')
def photo_feed():
    query = Photo.query().order(-Photo.date)
    data = query.fetch(RSS_LIMIT)
    last_modified = rfc822_date(data[0].date)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    str = u'<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel>'
    str += u'<title>АNDрејевићи photo album</title>'
    str += u'<link>http://%s/photos</link>' % settings.HOST_NAME
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
        str += u'<enclosure url="http://%s%s/small" length="%s" type="image/jpeg"></enclosure>' % (settings.HOST_NAME, item.get_absolute_url(), len(item.picture.get().small))
        str += u'<link>http://%s%s</link>' % (settings.HOST_NAME, item.get_absolute_url())
        str += u'<author>%s</author>' % item.author.email()
        str += u'<pubDate>%s</pubDate>' % rfc822_date(item.date)
        str += u'<guid isPermaLink="true">http://%s%s</guid>' % (settings.HOST_NAME, item.get_absolute_url())
        text = ','.join(item.tags)
        str += u'<category>%s</category>' % escape(text)
        str += u'</item>'
    str += u'</channel></rss>'

    response = HttpResponse(mimetype='application/rss+xml', content_type='application/rss+xml')
    response['Last-Modified'] = last_modified
    response['ETag'] = hashlib.md5(last_modified).hexdigest()
    response['Expires'] = rfc822_date(expires)
    response['Cache-Control'] = 'max-age=86400'
    response.write(str)
    return response

@vary_on_headers('Host')
def entry_feed():
    query = Entry.query().order(-Entry.date)
    data = query.fetch(RSS_LIMIT)
    last_modified = rfc822_date(data[0].date)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    str = u'<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel>'
    str += u'<title>АNDрејевићи blog</title>'
    str += u'<link>http://%s/entries</link>' % settings.HOST_NAME
    str += u'<lastBuildDate>%s</lastBuildDate>' % last_modified
    str += u'<description>Latest blog entries from the site</description>'

    for item in data:
        str += u'<item><title>%s</title>' % escape(item.headline)
        str += u'<description>%s</description>' % escape(item.summary)
        str += u'<link>http://%s%s</link>' % (settings.HOST_NAME, item.get_absolute_url())
        str += u'<author>%s</author>' % item.author.email()
        str += u'<pubDate>%s</pubDate>' % rfc822_date(item.date)
        str += u'<guid isPermaLink="true">http://%s%s</guid>' % (settings.HOST_NAME, item.get_absolute_url())
        text = ','.join(item.tags)
        str += u'<category>%s</category>' % escape(text)
        str += u'</item>'
    str += u'</channel></rss>'

    response = HttpResponse(mimetype='application/rss+xml', content_type='application/rss+xml')
    response['Last-Modified'] = last_modified
    response['ETag'] = hashlib.md5(last_modified).hexdigest()
    response['Expires'] = rfc822_date(expires)
    response['Cache-Control'] = 'max-age=86400'
    response.write(str)
    return response

def rss(request, kind):
    if kind == 'photo': return photo_feed()
    elif kind == 'entry': return entry_feed()

def sitemap(request):
    response = HttpResponse(mimetype='application/xml')
    out = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    head = '<url><loc>%s</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>'
    row = '<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.3</priority></url>'

    loc = 'http://%s%s' % (settings.HOST_NAME, '/photos')
    out += head % loc
    for item in Photo.query().order(-Photo.date):
        loc = 'http://%s%s' % (settings.HOST_NAME, item.get_absolute_url())
        out += row % (loc, item.date.date())

    loc = 'http://%s%s' % (settings.HOST_NAME, '/entries')
    out += head % loc
    for item in Entry.query().order(-Entry.date):
        loc = 'http://%s%s' % (settings.HOST_NAME, item.get_absolute_url())
        out += row % (loc, item.date.date())

    out += '</urlset>'
    response.write(out)
    return response
