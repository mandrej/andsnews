from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute
from views import Index, DeleteHandler, handle_403, handle_404, handle_500,  \
    latest, RenderCloud, auto_complete, sitemap, visualize, Find, Chat, Send, rss
from settings import DEBUG

CONFIG = {
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
}

app = WSGIApplication([
    PathPrefixRoute('/photos', [
        Route('/', handler='photo.views.Index', name='photos'),
        Route('/add', handler='photo.views.Add', name='photo_add'),
        Route('/<slug>/edit', handler='photo.views.Edit', name='photo_edit'),
        Route('/<slug>', handler='photo.views.Detail', name='photo'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/<slug>', handler='photo.views.Detail'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/', handler='photo.views.Index'),
    ]),
    PathPrefixRoute('/entries', [
        Route('/', handler='entry.views.Index', name='entries'),
        Route('/add', handler='entry.views.Add', name='entry_add'),
        Route('/<slug>/edit', handler='entry.views.Edit', name='entry_edit'),
        Route('/<field:(tags|date|author)>/<value>/', handler='entry.views.Index'),
        Route('/image/<slug>/<size:(small|normal)>', handler='entry.views.thumb'),
        Route('/<slug>', handler='entry.views.Detail', name='entry'),
    ]),
    PathPrefixRoute('/comments', [
        Route('/', handler='comment.views.Index', name='comments'),
        Route('/<safekey>/add', handler='comment.views.Add', name='comment_add'),
        Route('/<field:(forkind|date|author)>/<value>/', handler='comment.views.Index'),
    ]),
    PathPrefixRoute('/news', [
        Route('/', handler='news.views.Index', name='feeds'),
        Route('/add', handler='news.views.Add', name='feed_add'),
        Route('/<slug>/edit', handler='news.views.Edit', name='feed_edit'),
        Route('/<slug>', handler='news.views.Detail', name='feed'),
        Route('/<field:tags>/<value>/', handler='news.views.Index'),
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

        Route('/memcache', handler='admin.views.memcache_content'),
        Route('/memcache/<key>/build', handler='admin.views.build'),
        Route('/memcache/<key>/create', handler='admin.views.create'),
        Route('/memcache/<key>/delete', handler='admin.views.memcache_delete'),
#        Route('/thumbnail/color', handler='admin.views.thumbnail_color'),
    ]),
    Route('/filter/<key>/<value>', handler=RenderCloud),
    Route('/filter/<key>', handler=RenderCloud),
    Route('/search', handler=Find),
    Route('/_ah/xmpp/message/chat/', handler=Chat),
    Route('/send', handler=Send),
    Route('/sitemap.xml', handler=sitemap),
    Route('/visualize/<key>', handler=visualize),
    Route('/rss/<kind:(photo|entry)>.xml', handler=rss),
    Route('/complete/<kind:photo|entry|feed>/<field:tags|lens>', handler=auto_complete),

    Route('/<safekey>/delete', handler=DeleteHandler, name='delete'),
    Route('/latest', handler=latest),
    Route('/setlang', handler='common.SetLanguage'),
    Route('/sign', handler='common.sign_helper'),
    Route('/', handler=Index, name='start'),
], config=CONFIG, debug=DEBUG)

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500