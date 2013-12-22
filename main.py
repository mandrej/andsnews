__author__ = 'milan'

from webapp2 import WSGIApplication, Route, SimpleRoute
from webapp2_extras.routes import PathPrefixRoute
from handlers import auto_complete, Index, Latest, SetLanguage, Sign, Find, Chat, Rss, \
    DeleteHandler, RenderCloud, RenderGraph, SiteMap, AppCache
from config import CONFIG, DEVEL


app = WSGIApplication(
    [SimpleRoute(r'^/photos/?$', handler='views.photo.Index'),
     PathPrefixRoute('/photos', [
         Route('/', handler='views.photo.Index', name='photo_all'),
         Route('/add', handler='views.photo.Add', name='photo_add'),
         Route('/<slug>/edit', handler='views.photo.Edit', name='photo_edit'),
         Route('/<slug>/palette', handler='views.photo.Palette', name='palette'),
         Route('/<slug>', handler='views.photo.Detail', name='photo'),
         Route('/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/<slug>',
               handler='views.photo.Detail', name='photo_filter'),
         Route('/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/',
               handler='views.photo.Index', name='photo_filter_all'),
     ]),
     SimpleRoute(r'^/entries/?$', handler='views.entry.Index'),
     PathPrefixRoute('/entries', [
         Route('/', handler='views.entry.Index', name='entry_all'),
         Route('/add', handler='views.entry.Add', name='entry_add'),
         Route('/<slug>/edit', handler='views.entry.Edit', name='entry_edit'),
         Route('/<field:(tags|date|author)>/<value>/', handler='views.entry.Index', name='entry_filter_all'),
         Route('/image/<slug>/<size:(small|normal)>', handler='views.entry.thumb', name='entry_image'),
         Route('/<slug>', handler='views.entry.Detail', name='entry'),
     ]),
     SimpleRoute(r'^/comments/?$', handler='views.comment.Index'),
     PathPrefixRoute('/comments', [
         Route('/', handler='views.comment.Index', name='comment_all'),
         Route('/<field:(forkind|date|author)>/<value>/', handler='views.comment.Index', name='comment_filter_all'),
     ]),
     SimpleRoute(r'^/news/?$', handler='views.news.Index'),
     PathPrefixRoute('/news', [
         Route('/', handler='views.news.Index', name='feed_all'),
         Route('/add', handler='views.news.Add', name='feed_add'),
         Route('/<slug>/edit', handler='views.news.Edit', name='feed_edit'),
         Route('/<slug>', handler='views.news.Detail', name='feed'),
         Route('/<field:tags>/<value>/', handler='views.news.Index', name='feed_filter_all'),
     ]),
     SimpleRoute(r'^/admin/?$', handler='views.admin.Index'),
     PathPrefixRoute('/admin', [
         Route('/', handler='views.admin.Index'),
         Route('/comments', handler='views.admin.Comments'),
         Route('/feeds', handler='views.admin.Feeds'),
         Route('/counters', handler='views.admin.Counters'),
         Route('/spectra', handler='views.admin.Spectra'),

         Route('/blobs', handler='views.admin.Blobs'),
         Route('/blobs/<field:date>/<value>', handler='views.admin.Blobs'),
         Route('/images', handler='views.admin.Images'),
         Route('/images/<field:date>/<value>', handler='views.admin.Images'),

         Route('/memcache/', handler='views.admin.Cache', methods=['GET']),
         Route('/memcache/<mem_key>', handler='views.admin.Cache', methods=['PUT', 'DELETE']),
     ]),
     Route('/filter/<mem_key>/<value>', handler=RenderCloud),
     Route('/filter/<mem_key>', handler=RenderCloud),
     Route('/visualize/<mem_key>', handler=RenderGraph),
     Route('/complete/<mem_key>', handler=auto_complete),

     Route('/sitemap.xml', handler=SiteMap),
     Route('/rss/<kind:(photo|entry)>.xml', handler=Rss),
     Route('/_ah/xmpp/message/chat/', handler=Chat),

     Route('/<safe_key>/delete', handler=DeleteHandler, name='delete'),
     Route('/<safe_key>/add', handler='views.comment.Add', name='comment_add'),
     Route('/search', handler=Find),
     #Route('/send', handler=Send),
     Route('/latest', handler=Latest),
     #Route('/metajson', handler=PhotoMeta),
     Route('/cache.appcache', handler=AppCache),
     Route('/setlang', handler=SetLanguage),
     Route('/sign', handler=Sign),
     Route('/', handler=Index, name='start'),
    ], config=CONFIG, debug=DEVEL)