from webapp2 import WSGIApplication, SimpleRoute, Route
from webapp2_extras.routes import PathPrefixRoute, MultiRoute
from views import Index, DeleteHandler, handle_403, handle_404, handle_500,  \
    latest, RenderCloud, auto_complete, sitemap, visualize, Find, Chat, Send, rss
from settings import DEBUG

CONFIG = {
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
#    'locales' : ['en_US', 'sr_RS']
}

app = WSGIApplication([
    SimpleRoute(r'^/photos/?$', handler='photo.views.Index'),
    PathPrefixRoute('/photos', [
        Route('/add', handler='photo.views.Add'),
        Route('/<slug>/edit', handler='photo.views.Edit'),
        Route('/<slug>', handler='photo.views.Detail'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/<slug>', handler='photo.views.Detail'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>', handler='photo.views.Index'),
        Route('/<slug>/<size:(small|normal)>', handler='photo.views.thumb'), # TODO DEPRICATE
        ]),
    SimpleRoute(r'^/entries/?$', handler='entry.views.Index'),
    PathPrefixRoute('/entries', [
#        Route('/add', handler='entry.views.Add'),
#        Route('/<slug>/edit', handler='entry.views.Edit'),
        Route('/image/<slug>/<size:(small|normal)>', handler='entry.views.thumb'), # TODO DEPRICATE
        Route('/<slug>', handler='entry.views.Detail'),
        ]),
    SimpleRoute(r'^/comments/?$', handler='comment.views.Index'),
    PathPrefixRoute('/comments', [
        Route('/<safekey>/add', handler='comment.views.Add'),
        ]),
    SimpleRoute('^/news/?$', handler='news.views.Index'),
    PathPrefixRoute('/news', [
        Route('/add', handler='news.views.Add'),
        Route('/<slug>/edit', handler='news.views.Edit'),
        Route('/<slug>', handler='news.views.Detail'),
        ]),
    SimpleRoute(r'^/admin/?$', handler='admin.views.Index'),
    PathPrefixRoute('/admin', [
        Route('/comments', handler='admin.views.Comments'),
        Route('/<kind:(photo)>/thumbnails/', handler='admin.views.Thumbnails'),
        Route('/<kind:(photo)>/thumbnails/<field:(date|hue|lum)>/<value>$', handler='admin.views.Thumbnails'),
        Route('/<kind:(entry)>/thumbnails/', handler='admin.views.Thumbnails', defaults={'per_page': 6}),
        Route('/<kind:(entry)>/thumbnails/<field:(date)>/<value>$', handler='admin.views.Thumbnails', defaults={'per_page': 6}),

        Route('/memcache$', handler='admin.views.memcahe_content'),
        Route('/memcache/<key>/build$', handler='admin.views.build'),
        Route('/memcache/<key>/create', handler='admin.views.create'),
        Route('/memcache/<key>/delete$', handler='admin.views.memcache_delete'),
        ]),
    Route('/filter/<key>/<value>', handler=RenderCloud),
    Route('/filter/<key>', handler=RenderCloud),
    Route('/search', handler=Find),
    Route('/_ah/xmpp/message/chat/', handler=Chat),
    Route('/send', handler=Send),
    Route('/sitemap\.xml', handler=sitemap),
    Route('/visualize/<key>', handler=visualize),
    Route('/rss/<kind:(photo|entry)>.xml', handler=rss),
    Route('/complete/<kind:photo|entry|feed>/<field:tags|lens>', handler=auto_complete),

    Route('/<safekey>/delete', handler=DeleteHandler),
    Route('/latest', handler=latest),
    Route('/setlang', 'common.SetLanguage'),
    Route('/sign', 'common.sign_helper'),
    Route('/', handler=Index),
    ], config=CONFIG, debug=DEBUG)

#app.error_handlers[403] = handle_403
#app.error_handlers[404] = handle_404
#app.error_handlers[500] = handle_500