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
        Route(r'/add', handler='photo.views.Add'),
        Route(r'/<slug>/edit', handler='photo.views.Edit'),
        Route(r'/<slug>', handler='photo.views.Detail'),
        Route(r'/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>/<slug>', handler='photo.views.Detail'),
        Route(r'/<field:(model|iso|eqv|lens|tags|date|author|hue|lum)>/<value>', handler='photo.views.Index'),
#        Route(r'/<slug>/<size:(small|normal)>', handler='photo.views.thumb'), # TODO DEPRICATE
        ]),
    SimpleRoute(r'^/entries/?$', handler='entry.views.Index'),
    PathPrefixRoute('/entries', [
#        Route(r'/add', handler='entry.views.Add'),
#        Route(r'/<slug>/edit', handler='entry.views.Edit'),
        Route(r'/image/<slug>/<size:(small|normal)>', handler='entry.views.thumb'), # TODO DEPRICATE
        Route(r'/<slug>', handler='entry.views.Detail'),
        ]),
    SimpleRoute(r'^/comments/?$', handler='comment.views.Index'),
    PathPrefixRoute('/comments', [
        Route(r'/<safekey>/add', handler='comment.views.Add'),
        ]),
    SimpleRoute(r'^/news/?$', handler='news.views.Index'),
    PathPrefixRoute('/news', [
        Route(r'/add', handler='news.views.Add'),
        Route(r'/<slug>/edit', handler='news.views.Edit'),
        Route(r'/<slug>', handler='news.views.Detail'),
        ]),
    PathPrefixRoute('/admin', [
        ]),
    Route(r'/filter/<key>/<value>', handler=RenderCloud),
    Route(r'/filter/<key>', handler=RenderCloud),
    Route(r'/search', handler=Find),
    Route(r'/_ah/xmpp/message/chat/', handler=Chat),
    Route(r'/send', handler=Send),
    Route(r'/sitemap\.xml', handler=sitemap),
    Route(r'/visualize/<key>', handler=visualize),
    Route(r'/rss/<kind:(photo|entry)>.xml', handler=rss),
    Route(r'/complete/<kind:photo|entry|feed>/<field:tags|lens>', handler=auto_complete),

    Route(r'/<safekey>/delete', handler=DeleteHandler),
    Route(r'/latest', handler=latest),
    Route(r'/setlang', 'common.SetLanguage'),
    Route(r'/sign', 'common.sign_helper'),
    Route(r'/', handler=Index),
    ], config=CONFIG, debug=DEBUG)

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500