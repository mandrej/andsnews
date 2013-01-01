from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute
from views import Index, latest, RenderCloud, auto_complete, sitemap, visualize, Find, Chat, Send, rss

config = {
    'webapp2_extras.i18n': {'translations_path': 'locale'},
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
#    'locales' : ['en_US', 'sr_RS']
}

app = WSGIApplication([
    PathPrefixRoute('/photos', [
        Route('/<field:model|iso|eqv|lens|tags|date|author|hue|lum>/<value:.+>/<slug:[-\w]+>', 'photo.views.Detail'),
        Route('/<slug:[-\w]+>/<size:small|normal>', 'photo.views.thumb'), # TODO DEPRICATED
        Route('/<slug:[-\w]+>/delete', 'photo.views.Delete'),
        Route('/<slug:[-\w]+>', 'photo.views.Detail'),
        ]),
    PathPrefixRoute('/entries', [
        ]),
    PathPrefixRoute('/comments', [
        ]),
    PathPrefixRoute('/news', [
        ]),
    PathPrefixRoute('/admin', [
        ]),
    Route('/photos', 'photo.views.Index'),
    Route('/filter/<key:\w+>/<value:.+>', handler=RenderCloud),
    Route('/filter/<key:\w+>', handler=RenderCloud),
    Route('/search', handler=Find),
    Route('/_ah/xmpp/message/chat/', handler=Chat),
    Route('/send', handler=Send),
    Route('/sitemap.xml', handler=sitemap),
    Route('/visualize/<key:\w+>', handler=visualize),
    Route('/rss/<kind:photo|entry>.xml', handler=rss),
    Route('/complete/<kind:photo|entry|feed>/<field:tags|lens>', handler=auto_complete),
    Route('/latest', handler=latest),
    Route('/', handler=Index),
    ], config=config, debug=True)