__author__ = 'milan'

import logging

from webapp2 import WSGIApplication, Route

from handlers import Complete, SetLanguage, Sign, DeleteHandler, RenderCloud, RenderGraph, SiteMap, SaveAsHandler
from config import CONFIG, DEVEL

logging.getLogger().setLevel(logging.INFO)

app = WSGIApplication([
    Route('/photos/', handler='views.photo.Index', name='photo_all'),
    Route('/photos/<slug>/palette', handler='views.photo.Palette', name='palette'),
    Route('/photos/item', handler='views.photo.Detail', name='photo'),
    Route('/photos/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/item',
          handler='views.photo.Detail', name='photo_filter'),
    Route('/photos/<field:(model|iso|eqv|lens|tags|date|author|color)>/<value>/',
          handler='views.photo.Index', name='photo_all_filter'),

    Route('/entries/', handler='views.entry.Index', name='entry_all'),
    Route('/entries/<field:(tags|date|author)>/<value>/',
          handler='views.entry.Index', name='entry_all_filter'),
    Route('/entries/image/<slug>/<size:(small|normal)>', handler='views.entry.thumb', name='entry_image'),
    Route('/entries/<slug>', handler='views.entry.Detail', name='entry'),

    Route('/admin/', handler='views.admin.Index', name='admin_all'),
    Route('/admin/photos/', handler='views.admin.Photos', name='photo_admin'),
    Route('/admin/photos/<field:(tags|author|date)>/<value>/',
          handler='views.admin.Photos', name='photo_admin_filter'),
    Route('/admin/photos/add', handler='views.photo.Add', name='photo_add'),
    Route('/admin/photos/<slug>', handler='views.photo.Edit', name='photo_edit'),
    Route('/admin/entries/', handler='views.admin.Entries', name='entry_admin'),
    Route('/admin/entries/<field:(tags|author|date)>/<value>/',
          handler='views.admin.Entries', name='entry_admin_filter'),
    Route('/admin/entries/add', handler='views.entry.Add', name='entry_add'),
    Route('/admin/entries/<slug>', handler='views.entry.Edit', name='entry_edit'),
    Route('/admin/counters/', handler='views.admin.Counters', name='counter_admin'),
    Route('/admin/counters/<field:(forkind|field|value)>/<value>/',
          handler='views.admin.Counters', name='counter_admin_filter'),
    Route('/admin/memcache/', handler='views.admin.Cache', methods=['GET']),
    Route('/admin/memcache/<mem_key>', handler='views.admin.Cache', methods=['PUT', 'DELETE']),
    Route('/admin/background/<job>', handler='views.admin.DatastoreBackground', name='datastore_background'),

    Route('/filter/<mem_key>/<value>', handler=RenderCloud),
    Route('/filter/<mem_key>', handler=RenderCloud),
    Route('/visualize/<mem_key>', handler=RenderGraph),
    Route('/complete/<mem_key>', handler=Complete),

    Route('/sitemap.xml', handler=SiteMap),
    Route('/<safe_key>/download', handler=SaveAsHandler, name='download'),
    Route('/<safe_key>/delete', handler=DeleteHandler, name='delete'),
    Route('/setlang', handler=SetLanguage),
    Route('/sign', handler=Sign),
    Route('/', handler='views.photo.Index', name='start'),
    ], config=CONFIG, debug=DEVEL)