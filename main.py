from webapp2 import WSGIApplication, Route

from views import api
from views.config import DEVEL
app = WSGIApplication([
    Route(r'/api/filters', handler=api.PhotoFilters, methods=['GET']),
    Route(r'/api/suggest/<mem_key>', handler=api.Suggest, methods=['GET']),
    Route(r'/api/search/<find>', handler=api.Find, methods=['GET']),
    Route(r'/api/info', handler=api.Info, methods=['GET']),

    Route(r'/api/add', handler=api.Crud, methods=['POST']),
    Route(r'/api/edit/<safe_key>', handler=api.Crud, methods=['PUT']),
    Route(r'/api/delete/<safe_key>', handler=api.Crud, methods=['DELETE']),
    Route(r'/api/download/<safe_key>', handler=api.Download, methods=['GET']),

    Route(r'/api/reindex', handler=api.BackgroundIndex, methods=['POST']),
    Route(r'/api/unbound', handler=api.BackgroundUnbound, methods=['POST']),
    Route(r'/api/missing', handler=api.BackgroundDeleted, methods=['POST']),
    Route(r'/api/rebuild/<mem_key>', handler=api.BackgroundBuild, methods=['POST']),
    Route(r'/api/message', handler=api.Notify, methods=['POST']),
], debug=DEVEL)
