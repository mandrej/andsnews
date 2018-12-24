from webapp2 import WSGIApplication, Route

from views import api
from views.config import DEVEL
app = WSGIApplication([
    Route(r'/api/counter/<set:(filters|values)>', handler=api.Counters, methods=['GET']),
    Route(r'/api/search/<find>', handler=api.Find, methods=['GET']),

    Route(r'/api/add', handler=api.Crud, methods=['POST']),
    Route(r'/api/edit/<safe_key>', handler=api.Crud, methods=['PUT']),
    Route(r'/api/delete/<safe_key>', handler=api.Crud, methods=['DELETE']),
    Route(r'/api/download/<safe_key>', handler=api.Download, methods=['GET']),

    Route(r'/api/message', handler=api.Notify, methods=['POST']),
    Route(r'/api/<verb:(rebuild)>/<field>', handler=api.BackgroundRunner, methods=['POST']),
    Route(r'/api/<verb:(reindex|unbound|missing|fix)>', handler=api.BackgroundRunner, methods=['POST']),
], debug=DEVEL)
