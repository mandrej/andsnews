from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute
from views import Index, latest, RenderCloud, auto_complete, sitemap, visualize, Find, Chat, Send, rss

config = {
    'webapp2_extras.jinja2' : {'template_path': ['templates'],
                               'environment_args': {'extensions': ['jinja2.ext.i18n', 'jinja2.ext.with_']}},
    'webapp2_extras.i18n': {'translations_path': 'locale'},
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
#    'locales' : ['en_US', 'sr_RS']
}

app = WSGIApplication([
    PathPrefixRoute('/photos', [
        Route('/<field:model|iso|eqv|lens|tags|date|author|hue|lum>/<value:.+>/<slug:[-\w]+>', 'photo.views.Detail'),
        Route('/<slug:[-\w]+>/<size:small|normal>', 'photo.views.thumb'), # TODO DEPRICATE
        Route('/<slug:[-\w]+>/delete', 'photo.views.Delete'),
        Route('/<slug:[-\w]+>', 'photo.views.Detail'),
        ]),
    PathPrefixRoute('/entries', [
        Route('/image/<slug:[-\w]+>/<size:small|normal>', 'entry.views.thumb'), # TODO DEPRICATE
        Route('/<slug:[-\w]+>/delete', 'entry.views.Delete'),
        Route('/<slug:[-\w]+>', 'entry.views.Detail'),
        ]),
    PathPrefixRoute('/comments', [
        Route('/<safekey:\w+>/delete', 'comment.views.Delete'),
        ]),
    PathPrefixRoute('/news', [
        Route('/<slug:[-\w]+>/delete', 'news.views.Delete'),
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

    Route('/photos', 'photo.views.Index'),
    Route('/entries', 'entry.views.Index'),
    Route('/comments', 'comment.views.Index'),
    Route('/news', 'news.views.Index'),
    Route('/latest', handler=latest),
    Route('/setlang', 'common.SetLanguage'),
    Route('/sign', 'common.sign_helper'),
    Route('/', handler=Index),
    ], config=config, debug=True)