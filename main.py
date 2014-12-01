__author__ = 'milan'

from webapp2 import WSGIApplication, Route, SimpleRoute
from webapp2_extras.routes import PathPrefixRoute
from handlers import Index, Complete, SetLanguage, Sign, Find, Chat, Rss, \
    DeleteHandler, RenderCloud, RenderGraph, SiteMap, PhotoMeta, Invalidate, SaveAsHandler
from config import CONFIG, DEVEL


app = WSGIApplication([
    SimpleRoute(r'^/photos/?$', handler='views.photo.Index'),
    PathPrefixRoute('/photos', [
        Route('/page/<page:\d+>', handler='views.photo.Index', name='photo_all'),
        Route('/<slug>/palette', handler='views.photo.Palette', name='palette'),
        Route('/<slug>', handler='views.photo.Detail', name='photo'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/<slug>',
              handler='views.photo.Detail', name='photo_filter'),
        Route('/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/page/<page:\d+>',
              handler='views.photo.Index', name='photo_all_filter'),
        ]),
    SimpleRoute(r'^/entries/?$', handler='views.entry.Index'),
    PathPrefixRoute('/entries', [
        Route('/page/<page:\d+>', handler='views.entry.Index', name='entry_all'),
        Route('/<field:(tags|date|author)>/<value>/page/<page:\d+>',
              handler='views.entry.Index', name='entry_all_filter'),
        Route('/image/<slug>/<size:(small|normal)>', handler='views.entry.thumb', name='entry_image'),
        Route('/<slug>', handler='views.entry.Detail', name='entry'),
    ]),
    SimpleRoute(r'^/comments/?$', handler='views.comment.Index'),
    PathPrefixRoute('/comments', [
        Route('/page/<page:\d+>', handler='views.comment.Index', name='comment_all'),
        Route('/<field:(forkind|date|author)>/<value>/page/<page:\d+>',
              handler='views.comment.Index', name='comment_all_filter'),
    ]),
    SimpleRoute(r'^/news/?$', handler='views.news.Index'),
    PathPrefixRoute('/news', [
        Route('/page/<page:\d+>', handler='views.news.Index', name='feed_all'),
        Route('/<slug>', handler='views.news.Detail', name='feed'),
        Route('/<field:tags>/<value>/page/<page:\d+>', handler='views.news.Index', name='feed_all_filter'),
    ]),
    SimpleRoute(r'^/admin/?$', handler='views.admin.Index'),
    PathPrefixRoute('/admin', [
        Route('/', handler='views.admin.Index', name='admin_all'),
        Route('/counters/page/<page:\d+>', handler='views.admin.Counters', name='counter_admin'),
        Route('/spectra', handler='views.admin.Spectra'),
        PathPrefixRoute('/photos', [
            Route('/page/<page:\d+>', handler='views.admin.Photos', name='photo_admin'),
            Route('/<field:date>/<value>/page/<page:\d+>', handler='views.admin.Photos', name='photo_admin_filter'),
            Route('/add', handler='views.photo.Add', name='photo_add'),
            Route('/<slug>', handler='views.photo.Edit', name='photo_edit'),
        ]),
        PathPrefixRoute('/entries', [
            Route('/page/<page:\d+>', handler='views.admin.Entries', name='entry_admin'),
            Route('/<field:date>/<value>/page/<page:\d+>', handler='views.admin.Entries', name='entry_admin_filter'),
            Route('/add', handler='views.entry.Add', name='entry_add'),
            Route('/<slug>', handler='views.entry.Edit', name='entry_edit'),
        ]),
        PathPrefixRoute('/feeds', [
            Route('/', handler='views.admin.Feeds', name='feed_admin'),
            Route('/add', handler='views.news.Add', name='feed_add'),
            Route('/<slug>', handler='views.news.Edit', name='feed_edit'),
        ]),
        PathPrefixRoute('/comments', [
            Route('/page/<page:\d+>', handler='views.admin.Comments', name='comment_admin'),
        ]),
        Route('/memcache/', handler='views.admin.Cache', methods=['GET']),
        Route('/memcache/<mem_key>', handler='views.admin.Cache', methods=['PUT', 'DELETE']),
        # MapReduce Jobs
        Route('/background/<job>', handler='views.admin.DatastoreBackground', name='datastore_background'),
    ]),
    Route('/filter/<mem_key>/<value>', handler=RenderCloud),
    Route('/filter/<mem_key>', handler=RenderCloud),
    Route('/visualize/<mem_key>', handler=RenderGraph),
    Route('/complete/<mem_key>', handler=Complete),

    Route('/sitemap.xml', handler=SiteMap),
    Route('/rss/<kind:(photo|entry)>.xml', handler=Rss),
    Route('/_ah/xmpp/message/chat/', handler=Chat),

    Route('/<safe_key>/download', handler=SaveAsHandler, name='download'),
    Route('/<safe_key>/delete', handler=DeleteHandler, name='delete'),
    Route('/<safe_key>/add', handler='views.comment.Add', name='comment_add'),
    Route('/search/<page:\d+>', handler=Find, name='search'),
    Route('/photometa', handler=PhotoMeta),
    Route('/setlang', handler=SetLanguage),
    Route('/invalidate', handler=Invalidate),
    Route('/sign', handler=Sign),
    Route('/', handler=Index, name='start'),
    ], config=CONFIG, debug=DEVEL)