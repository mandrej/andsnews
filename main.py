from webapp2 import WSGIApplication, Route

from config import DEVEL

app = WSGIApplication([
    Route(r'/api/suggest/<mem_key>', handler='views.api.Suggest'),
    Route(r'/api/filters', handler='views.api.PhotoFilters'),
    Route(r'/api/search/<find>', handler='views.api.Find'),

    Route(r'/api/<kind:(photo|entry)>', handler='views.api.Collection'),
    Route(r'/api/<kind:(photo|entry)>/<field:(date|tags|color|model|author|show)>/<value>',
          handler='views.api.Collection'),

    Route(r'/api/<kind:(photo|entry)>/add', handler='views.api.Crud', methods=['GET', 'POST']),
    Route(r'/api/<kind:(photo|entry)>/edit/<safe_key>', handler='views.api.Crud', methods=['GET', 'PUT']),
    Route(r'/api/delete/<safe_key>', handler='views.api.Crud', methods=['DELETE']),
    Route(r'/api/download/<safe_key>', handler='views.api.Download'),

    Route(r'/api/info', handler='views.api.Info'),
    Route(r'/api/index/<kind>', handler='views.api.BackgroundIndex', methods=['POST']),
    Route(r'/api/unbound/<kind>', handler='views.api.BackgroundUnbound', methods=['POST']),
    Route(r'/api/fix/<kind>', handler='views.api.BackgroundFix', methods=['POST']),
    Route(r'/api/rebuild/<mem_key>', handler='views.api.BackgroundBuild', methods=['POST']),
], debug=DEVEL)
