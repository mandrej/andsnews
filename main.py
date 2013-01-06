from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute
from views import Index, DeleteHandler, latest, RenderCloud, auto_complete, sitemap, visualize, Find, Chat, Send, rss
from settings import DEBUG

config = {
    'webapp2_extras.jinja2' : {'template_path': ['templates'],
                               'environment_args': {'extensions': ['jinja2.ext.i18n', 'jinja2.ext.with_']}},
    'webapp2_extras.i18n': {'translations_path': 'locale'},
    'webapp2_extras.sessions': {'secret_key': 'iasbj*6WZ2'},
#    'locales' : ['en_US', 'sr_RS']
}

app = WSGIApplication([
    Route('/photos', 'photo.views.Index'),
    PathPrefixRoute('/photos', [
        Route('/add', 'photo.views.Add'),
        Route('/<slug:[-\w]+>/edit', 'photo.views.Edit'),
        Route('/<slug:[-\w]+>', 'photo.views.Detail'),
        Route('/<field:model|iso|eqv|lens|tags|date|author|hue|lum>/<value:.+>/<slug:[-\w]+>', 'photo.views.Detail'),
        Route('/<slug:[-\w]+>/<size:small|normal>', 'photo.views.thumb'), # TODO DEPRICATE
        ]),
    Route('/entries', 'entry.views.Index'),
    PathPrefixRoute('/entries', [
#        Route('/add', 'entry.views.Add'),
#        Route('/<slug:[-\w]+>/edit', 'entry.views.Edit'),
        Route('/image/<slug:[-\w]+>/<size:small|normal>', 'entry.views.thumb'), # TODO DEPRICATE
        Route('/<slug:[-\w]+>', 'entry.views.Detail'),
        ]),
    Route('/comments', 'comment.views.Index'),
    PathPrefixRoute('/comments', [
        Route('/validate', handler='comment.views.Validate'),
        Route('/<safekey:\w+>/add', handler='comment.views.Add'),
        ]),
    Route('/news', 'news.views.Index'),
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
    ], config=config, debug=DEBUG)