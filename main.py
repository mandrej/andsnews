from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute
from views import Index, latest, RenderCloud, RenderGraph, auto_complete, sitemap, Find, Chat, Send, rss
from common import handle_403, handle_404, handle_500
from settings import DEBUG

CONFIG = {
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
}

app = WSGIApplication([
    PathPrefixRoute('/photos', [
        Route('/', handler='photo.views.Index', name='photo_all'),
        Route('/add', handler='photo.views.Add', name='photo_add'),
        Route('/<slug>/edit', handler='photo.views.Edit', name='photo_edit'),
        Route('/<slug>', handler='photo.views.Detail', name='photo'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/<slug>',
              handler='photo.views.Detail', name='photo_filter'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/',
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

        Route('/blobs', handler='admin.views.Blobs'),
        Route('/blobs/<field:date>/<value>', handler='admin.views.Blobs'),
        Route('/images', handler='admin.views.Images'),
        Route('/images/<field:date>/<value>', handler='admin.views.Images'),

        Route('/memcache/', handler='admin.views.Cache', methods=['GET']),
        Route('/memcache/<key>', handler='admin.views.Cache', methods=['PUT', 'DELETE']),
        # Route('/thumbnail/color', handler='admin.views.thumbnail_color'),
    ]),
    Route('/filter/<key>/<value>', handler=RenderCloud),
    Route('/filter/<key>', handler=RenderCloud),
    Route('/visualize/<key>', handler=RenderGraph),
    Route('/search', handler=Find),
    Route('/_ah/xmpp/message/chat/', handler=Chat),
    Route('/send', handler=Send),
    Route('/sitemap.xml', handler=sitemap),
    Route('/rss/<kind:(photo|entry)>.xml', handler=rss),
    Route('/complete/<kind:photo|entry|feed>/<field:tags|lens>', handler=auto_complete),

    Route('/<safekey>/delete', handler='common.DeleteHandler', name='delete'),
    Route('/<safekey>/add', handler='comment.views.Add', name='comment_add'),
    Route('/latest', handler=latest),
    Route('/setlang', handler='common.SetLanguage'),
    Route('/sign', handler='common.Sign'),
    Route('/', handler=Index, name='start'),
], config=CONFIG, debug=DEBUG)

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500