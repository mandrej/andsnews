from webapp2 import WSGIApplication, Route
from graphene_gae.webapp2 import GraphQLHandler
from views import api
from views.config import DEVEL
from views.schema import schema

config = {
    'graphql_schema': schema,
    'graphql_pretty': True
}

app = WSGIApplication([
    Route(r'/graphql', handler=GraphQLHandler),
    Route(r'/api/add', handler=api.Crud, methods=['POST']),
    Route(r'/api/download/<safe_key>', handler=api.Download, methods=['GET']),

    Route(r'/api/message', handler=api.Notify, methods=['POST']),
    Route(r'/api/<verb:(rebuild)>/<field>', handler=api.BackgroundRunner, methods=['POST']),
    Route(r'/api/<verb:(reindex|unbound|missing)>', handler=api.BackgroundRunner, methods=['POST']),
], debug=DEVEL, config=config)
