from webapp2 import WSGIApplication, SimpleRoute, Route
from webapp2_extras.routes import PathPrefixRoute, MultiRoute
from views import Index, DeleteHandler, handle_403, handle_404, handle_500,  \
    latest, RenderCloud, auto_complete, sitemap, visualize, Find, Chat, Send, rss
from settings import DEBUG

CONFIG = {
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
}

app = WSGIApplication([
    SimpleRoute(r'^/photos/?$', handler='photo.views.Index'),
    PathPrefixRoute('/photos', [
        Route('/add', handler='photo.views.Add'),
        Route('/<slug>/edit', handler='photo.views.Edit'),
        Route('/<slug>/<idx:\d+>', handler='photo.views.Detail'),
        Route('/<slug>', handler='photo.views.Detail'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/<slug>/<idx:\d+>', handler='photo.views.Detail'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/<slug>', handler='photo.views.Detail'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>', handler='photo.views.Index'),
        ]),
    SimpleRoute(r'^/entries/?$', handler='entry.views.Index'),
    PathPrefixRoute('/entries', [
        Route('/add', handler='entry.views.Add'),
        Route('/<slug>/edit', handler='entry.views.Edit'),
        Route('/<field:(tags|date|author)>/<value>', handler='entry.views.Index'),
        Route('/image/<slug>/<size:(small|normal)>', handler='entry.views.thumb'),
        Route('/<slug>', handler='entry.views.Detail'),
        ]),
    SimpleRoute(r'^/comments/?$', handler='comment.views.Index'),
    PathPrefixRoute('/comments', [
        Route('/<safekey>/add', handler='comment.views.Add'),
        Route('/<field:(forkind|date|author)>/<value>', handler='comment.views.Index'),
        ]),
    SimpleRoute('^/news/?$', handler='news.views.Index'),
    PathPrefixRoute('/news', [
        Route('/add', handler='news.views.Add'),
        Route('/<slug>/edit', handler='news.views.Edit'),
        Route('/<slug>', handler='news.views.Detail'),
        Route('/<field:(tags)>/<value>', handler='news.views.Index'),
        ]),
    SimpleRoute(r'^/admin/?$', handler='admin.views.Index'),
    PathPrefixRoute('/admin', [
        Route('/comments', handler='admin.views.Comments'),
        Route('/comments/save', 'admin.views.comment_save'),
        Route('/comments/delete', 'admin.views.comment_delete'),

        Route('/feeds', handler='admin.views.Feeds'),
        Route('/counters', handler='admin.views.Counters'),

        Route('/<kind:(photo)>/thumbnails', handler='admin.views.Thumbnails'),
        Route('/<kind:(photo)>/thumbnails/<field:(date|hue|lum)>/<value>$', handler='admin.views.Thumbnails'),
        Route('/<kind:(entry)>/thumbnails', handler='admin.views.Thumbnails', defaults={'per_page': 6}),
        Route('/<kind:(entry)>/thumbnails/<field:(date)>/<value>$', handler='admin.views.Thumbnails', defaults={'per_page': 6}),

        Route('/memcache', handler='admin.views.memcache_content'),
        Route('/memcache/<key>/build', handler='admin.views.build'),
        Route('/memcache/<key>/create', handler='admin.views.create'),
        Route('/memcache/<key>/delete', handler='admin.views.memcache_delete'),

        Route('/thumbnail/delete', 'admin.views.thumbnail_delete'),
        Route('/thumbnail/make', 'admin.views.thumbnail_make'),
        Route('/thumbnail/color', 'admin.views.thumbnail_color'),

        Route('/photo/info/<safekey>', 'admin.views.info'),
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

    Route('/<safekey>/delete', handler=DeleteHandler),
    Route('/latest', handler=latest),
    Route('/setlang', 'common.SetLanguage'),
    Route('/sign', 'common.sign_helper'),
    Route('/', handler=Index),
    ], config=CONFIG, debug=DEBUG)

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500