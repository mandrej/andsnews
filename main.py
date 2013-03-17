import logging
from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute
from views import Index, latest, auto_complete, sitemap, Chat, Send, rss
from handlers import DeleteHandler, SetLanguage, Sign, RenderCloud, RenderGraph, Find, handle_403, handle_404, handle_500
from settings import DEVEL

CONFIG = {
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
}

app = WSGIApplication([
    PathPrefixRoute('/photos', [
        Route('/', handler='photo.views.Index', name='photo_all'),
        Route('/add', handler='photo.views.Add', name='photo_add'),
        Route('/<slug>/edit', handler='photo.views.Edit', name='photo_edit'),
        Route('/<slug>/palette', handler='photo.views.Palette', name='palette'),
        Route('/<slug>', handler='photo.views.Detail', name='photo'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/<slug>',
              handler='photo.views.Detail', name='photo_filter'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/',
              handler='photo.views.Index', name='photo_filter_all'),
    ]),
    PathPrefixRoute('/entries', [
        Route('/', handler='entry.views.Index', name='entry_all'),
        Route('/add', handler='entry.views.Add', name='entry_add'),
        Route('/<slug>/edit', handler='entry.views.Edit', name='entry_edit'),
        Route('/<field:(tags|date|author)>/<value>/', handler='entry.views.Index', name='entry_filter_all'),
        Route('/image/<slug>/<size:(small|normal)>', handler='entry.views.thumb', name='entry_image'),
        Route('/<slug>', handler='entry.views.Detail', name='entry'),
    ]),
    PathPrefixRoute('/comments', [
        Route('/', handler='comment.views.Index', name='comment_all'),
        Route('/<field:(forkind|date|author)>/<value>/', handler='comment.views.Index', name='comment_filter_all'),
    ]),
    PathPrefixRoute('/news', [
        Route('/', handler='news.views.Index', name='feed_all'),
        Route('/add', handler='news.views.Add', name='feed_add'),
        Route('/<slug>/edit', handler='news.views.Edit', name='feed_edit'),
        Route('/<slug>', handler='news.views.Detail', name='feed'),
        Route('/<field:tags>/<value>/', handler='news.views.Index', name='feed_filter_all'),
    ]),
    PathPrefixRoute('/admin', [
        Route('/', handler='admin.views.Index'),
        Route('/comments', handler='admin.views.Comments'),
        Route('/feeds', handler='admin.views.Feeds'),
        Route('/counters', handler='admin.views.Counters'),
        Route('/spectra', handler='admin.views.Spectra'),

        Route('/blobs', handler='admin.views.Blobs'),
        Route('/blobs/<field:date>/<value>', handler='admin.views.Blobs'),
        Route('/images', handler='admin.views.Images'),
        Route('/images/<field:date>/<value>', handler='admin.views.Images'),

        Route('/memcache/', handler='admin.views.Cache', methods=['GET']),
        Route('/memcache/<mem_key>', handler='admin.views.Cache', methods=['PUT', 'DELETE']),
    ]),
    Route('/filter/<mem_key>/<value>', handler=RenderCloud),
    Route('/filter/<mem_key>', handler=RenderCloud),
    Route('/visualize/<mem_key>', handler=RenderGraph),
    Route('/complete/<mem_key>', handler=auto_complete),

    Route('/sitemap.xml', handler=sitemap),
    Route('/rss/<kind:(photo|entry)>.xml', handler=rss),
    Route('/_ah/xmpp/message/chat/', handler=Chat),

    Route('/<safe_key>/delete', handler=DeleteHandler, name='delete'),
    Route('/<safe_key>/add', handler='comment.views.Add', name='comment_add'),
    Route('/search', handler=Find),
    Route('/send', handler=Send),
    Route('/latest', handler=latest),
    Route('/setlang', handler=SetLanguage),
    Route('/sign', handler=Sign),
    Route('/', handler=Index, name='start'),
], config=CONFIG, debug=DEVEL)

if DEVEL:
    logging.getLogger().setLevel(logging.DEBUG)

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500