from webapp2 import WSGIApplication, Route

from handlers import FrontPage, Complete, SetLanguage, Sign, Find, DeleteHandler, RenderCloud, \
    Plain, DrawGraph, SiteMap, SaveAsHandler
from config import CONFIG, DEVEL

app = WSGIApplication([
    # REST API
    Route(r'/api/<kind:(photo|entry)>', handler='views.api.Collection'),
    Route(r'/api/<kind:(photo|entry)>/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>',
          handler='views.api.Collection'),
    Route(r'/api/<kind:(photo|entry)>/<slug:[\w-]+>', handler='views.api.Record', methods=['GET']),

    Route(r'/api/entry/<slug:[\w-]+>', handler='views.api.EntryForm', methods=['PUT', 'POST']),
    Route(r'/api/photo/<slug:[\w-]+>', handler='views.api.PhotoForm', methods=['PUT', 'POST']),

    Route(r'/api/filter/<kind:(photo|entry)>', handler='views.api.KindFilter'),
    Route(r'/api/search/<find>', handler='views.api.Find'),

    Route(r'/api/download/<safe_key:[\w-]+>', handler='views.api.Download', name='download_url'),

    ###
    Route(r'/photos/', handler='views.photo.Index', name='photo_all'),
    Route(r'/photos/<slug:[\w-]+>', handler='views.photo.Detail', name='photo'),
    Route(r'/photos/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/<slug:[\w-]+>',
          handler='views.photo.Detail', name='photo_filter'),
    Route(r'/photos/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/',
          handler='views.photo.Index', name='photo_all_filter'),

    Route(r'/entries/', handler='views.entry.Index', name='entry_all'),
    Route(r'/entries/<field:(tags|date|author)>/<value>/',
          handler='views.entry.Index', name='entry_all_filter'),
    Route(r'/entries/image/<slug:[\w-]+>/<size:(small|normal)>', handler='views.entry.thumb', name='entry_image'),
    Route(r'/entries/<slug:[\w-]+>', handler='views.entry.Detail', name='entry'),

    Route(r'/admin/', handler='views.admin.Index', name='admin_all'),
    Route(r'/admin/photos/', handler='views.admin.Photos', name='photo_admin'),
    Route(r'/admin/photos/<field:(tags|author|date)>/<value>/',
          handler='views.admin.Photos', name='photo_admin_filter'),
    Route(r'/admin/photos/add', handler='views.photo.Add', name='photo_add'),
    Route(r'/admin/photos/<slug:[\w-]+>', handler='views.photo.Edit', name='photo_edit'),
    Route(r'/admin/photos/<slug:[\w-]+>/palette', handler='views.photo.Palette', name='palette'),
    Route(r'/admin/entries/', handler='views.admin.Entries', name='entry_admin'),
    Route(r'/admin/entries/<field:(tags|author|date)>/<value>/',
          handler='views.admin.Entries', name='entry_admin_filter'),
    Route(r'/admin/entries/add', handler='views.entry.Add', name='entry_add'),
    Route(r'/admin/entries/<slug:[\w-]+>', handler='views.entry.Edit', name='entry_edit'),
    Route(r'/admin/counters/', handler='views.admin.Counters', name='counter_admin'),
    Route(r'/admin/counters/<field:(forkind|field|value)>/<value>/',
          handler='views.admin.Counters', name='counter_admin_filter'),
    Route(r'/admin/memcache/', handler='views.admin.Cache', methods=['GET']),
    Route(r'/admin/memcache/<mem_key>', handler='views.admin.Cache'),
    Route(r'/admin/pie/<mem_key>', handler='views.admin.RenderPie'),
    Route(r'/admin/background/<job>', handler='views.admin.DatastoreBackground', name='datastore_background'),

    Route(r'/filter/<mem_key>/<value>', handler=RenderCloud),
    Route(r'/filter/<mem_key>', handler=RenderCloud),
    Route(r'/complete/<mem_key>', handler=Complete),

    Route(r'/<field:tags>/graph', handler=DrawGraph),
    Route(r'/graph', handler=Plain),
    Route(r'/sitemap.xml', handler=SiteMap),
    Route(r'/<safe_key:[\w-]+>/download', handler=SaveAsHandler, name='download'),
    Route(r'/<safe_key:[\w-]+>/delete', handler=DeleteHandler, name='delete'),
    Route('/search', handler=Find, name='search'),
    Route(r'/setlang', handler=SetLanguage),
    # Route(r'/about', handler=FrontPage, name='front'),
    Route(r'/sign', handler=Sign),
    # Route(r'/', handler='views.photo.Index', name='start'),
], config=CONFIG, debug=DEVEL)
