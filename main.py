from webapp2 import WSGIApplication, Route

from handlers import Sign, SiteMap
from config import CONFIG, DEVEL

app = WSGIApplication([
    # REST API
    Route(r'/api/suggest/<mem_key>', handler='views.api.Suggest'),
    Route(r'/api/filter/<kind:(photo|entry)>', handler='views.api.KindFilter'),
    Route(r'/api/search/<find>', handler='views.api.Find'),

    Route(r'/api/<kind:(photo|entry)>', handler='views.api.Collection'),
    Route(r'/api/<kind:(photo|entry)>/<field:(date|tags|model|author|show)>/<value>',
          handler='views.api.Collection'),

    Route(r'/api/<kind:(photo|entry)>/add', handler='views.api.Crud', methods=['GET', 'POST']),
    Route(r'/api/<kind:(photo|entry)>/edit/<safe_key>', handler='views.api.Crud', methods=['GET', 'PUT']),
    Route(r'/api/delete/<safe_key>', handler='views.api.Crud', methods=['DELETE']),
    Route(r'/api/download/<safe_key>', handler='views.api.Download', name='download_url'),

    Route(r'/api/memcache/<mem_key>', handler='views.api.Cache', methods=['PUT']),
    # REST API

    Route(r'/admin/', handler='views.admin.Index', name='admin_all'),
    Route(r'/admin/counters/', handler='views.admin.Counters', name='counter_admin'),
    Route(r'/admin/counters/<field:(forkind|field|value)>/<value>/',
          handler='views.admin.Counters', name='counter_admin_filter'),
    Route(r'/admin/memcache/', handler='views.admin.Cache', methods=['GET']),
    Route(r'/admin/memcache/<mem_key>', handler='views.admin.Cache'),
    Route(r'/admin/background/<job>', handler='views.admin.DatastoreBackground', name='datastore_background'),

    Route(r'/sitemap.xml', handler=SiteMap),
    # Route(r'/sign', handler=Sign),
    # Route(r'/', handler='views.photo.Index', name='start'),
], config=CONFIG, debug=DEVEL)
