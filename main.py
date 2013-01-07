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
    SimpleRoute(r'^/photos/?$', 'photo.views.Index'),
    PathPrefixRoute('/photos', [
        Route('/add', 'photo.views.Add'),
        Route('/<slug:[-\w]+>/edit', 'photo.views.Edit'),
        Route('/<slug:[-\w]+>', 'photo.views.Detail'),
        Route('/<field:model|iso|eqv|lens|tags|date|author|hue|lum>/<value:.+>/<slug:[-\w]+>', 'photo.views.Detail'),
        Route('/<slug:[-\w]+>/<size:small|normal>', 'photo.views.thumb'), # TODO DEPRICATE
        ]),
    SimpleRoute(r'^/entries/?$', 'entry.views.Index'),
    PathPrefixRoute('/entries', [
#        Route('/add', 'entry.views.Add'),
#        Route('/<slug:[-\w]+>/edit', 'entry.views.Edit'),
        Route('/image/<slug:[-\w]+>/<size:small|normal>', 'entry.views.thumb'), # TODO DEPRICATE
        Route('/<slug:[-\w]+>', 'entry.views.Detail'),
        ]),
    SimpleRoute(r'^/comments/?$', 'comment.views.Index'),
    PathPrefixRoute('/comments', [
        Route('/<safekey:\w+>/add', handler='comment.views.Add'),
        ]),
    SimpleRoute(r'^/news/?$', 'news.views.Index'),
    PathPrefixRoute('/news', [
        Route('/add', 'news.views.Add'),
        Route('/<slug:[-\w]+>/edit', 'news.views.Edit'),
        Route('/<slug:[-\w]+>', 'news.views.Detail'),
        ]),
    PathPrefixRoute('/admin', [
        ]),
    Route('/filter/<key:\w+>/<value:.+>', handler=RenderCloud),
    Route('/filter/<key:\w+>', handler=RenderCloud),
    Route('/search', handler=Find),
    Route('/_ah/xmpp/message/chat/', handler=Chat),
    Route('/send', handler=Send),
    Route('/sitemap.xml', handler=sitemap),
    Route('/visualize/<key:\w+>', handler=visualize),
    Route('/rss/<kind:photo|entry>.xml', handler=rss),
    Route('/complete/<kind:photo|entry|feed>/<field:tags|lens>', handler=auto_complete),

    Route('/<safekey:\w+>/delete', handler=DeleteHandler),
    Route('/latest', handler=latest),
    Route('/setlang', 'common.SetLanguage'),
    Route('/sign', 'common.sign_helper'),
    Route('/', handler=Index),
    ], config=CONFIG, debug=DEBUG)

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500