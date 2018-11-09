from webapp2 import WSGIApplication, Route

from views import api
from views.config import DEVEL
app = WSGIApplication([
    # Route(r'/api/start', handler=api.PhotoRecent),
    Route(r'/api/filters', handler=api.PhotoFilters),
    Route(r'/api/suggest/<mem_key>', handler=api.Suggest),
    Route(r'/api/search/<find>', handler=api.Find),

    # Route(r'/api/<kind:(photo|entry)>', handler=api.Collection),
    # Route(r'/api/<kind:(photo|entry)>/<field:(year|tags|color|model|author)>/<value>',
    #       handler=api.Collection),

    Route(r'/api/info', handler=api.Info, methods=['GET']),         # 1

    Route(r'/api/<kind:(photo|entry)>/add', handler=api.Crud, methods=['GET', 'POST']),
    Route(r'/api/<safe_key>', handler=api.Crud, methods=['GET']),   # 2
    Route(r'/api/<kind:(photo|entry)>/edit/<safe_key>', handler=api.Crud, methods=['PUT']),
    Route(r'/api/delete/<safe_key>', handler=api.Crud, methods=['DELETE']),
    Route(r'/api/download/<safe_key>', handler=api.Download, methods=['GET']),

    Route(r'/api/index/<kind>', handler=api.BackgroundIndex, methods=['POST']),
    Route(r'/api/unbound/<kind>', handler=api.BackgroundUnbound, methods=['POST']),
    Route(r'/api/fix/<kind>', handler=api.BackgroundDeleted, methods=['POST']),
    Route(r'/api/rebuild/<mem_key>', handler=api.BackgroundBuild, methods=['POST']),
    Route(r'/api/message', handler=api.Notify, methods=['POST']),

    # Route(r'/sitemap.xml', handler=api.SiteMap, methods=['GET'], name='sitemap'),
], debug=DEVEL)
