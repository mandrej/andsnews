#!/usr/bin/env python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main module for map-reduce implementation.

This module should be specified as a handler for mapreduce URLs in app.yaml:

  handlers:
  - url: /mapreduce(/.*)?
    login: admin
    script: mapreduce/main.py
"""



import wsgiref.handlers

#from google.appengine.ext import webapp
from mapreduce import handlers
from mapreduce import status
#from google.appengine.ext.webapp import util
import logging

import webapp2

try:
  from mapreduce.lib import pipeline
except ImportError:
  pipeline = None


STATIC_RE = r".*/([^/]*\.(?:css|js)|status|detail)$"

###################################################### mda 
from mapreduce import operation as op
from mapreduce import control
from mapreduce.model import MapreduceState
from google.appengine.ext import ndb
from models import Photo, Entry, Comment

def fixer(entity):
    pass
#    try:
#        delattr(entity, 'voters')
#        delattr(entity, 'sum')
#        delattr(entity, 'score')
#    except AttributeError:
#        pass
#    else:
#        yield op.db.Put(entity)

def indexer(key):
#    entity is oldkey for DatastoreKeyInputReader
#    <class 'google.appengine.api.datastore_types.Key'>
    nkey = ndb.Key.from_old_key(key)
#    <class 'google.appengine.ext.ndb.key.Key'>
    entity = nkey.get()
    entity.index_add()

#def process_tags(entity):
#    for tag in entity.tags:
#        yield op.counters.Increment(tag)
#
#class ReduceTags(webapp2.RequestHandler):
#    def get(self):
#        job_id = control.start_map(
#            'reduce_tags',
#            'mapreduce.main.process_tags',
#            'mapreduce.input_readers.DatastoreInputReader',
#            {'entity_kind': 'models.Photo', 'processing_rate': 5},
#            shard_count=4,
#            mapreduce_parameters={'done_callback': '/mapreduce/reduce_tags'}
#        )
#        self.redirect('mapreduce/status')
#
#    def post(self):
#        job_id = self.request.headers['Mapreduce-Id']
#        state = MapreduceState.get_by_job_id(job_id)
#        counters = state.counters_map.counters
#        del counters['mapper_calls']
#        del counters['mapper-walltime-msec']
#        coll = {}
#        for key, val in counters.iteritems():
#            coll[key] = val
#        logging.error(coll)
#        self.response.headers['Content-Type'] = 'text/plain'
#        self.response.out.write('done %s' % job_id)
#        return self.response

###################################################### mda

class RedirectHandler(webapp2.RequestHandler):
  """Redirects the user back to the status page."""

  def get(self):
    new_path = self.request.path
    if not new_path.endswith("/"):
      new_path += "/"
    new_path += "status"
    self.redirect(new_path)


def create_handlers_map():
  """Create new handlers map.

  Returns:
    list of (regexp, handler) pairs for WSGIApplication constructor.
  """
  pipeline_handlers_map = []

  if pipeline:
    pipeline_handlers_map = pipeline.create_handlers_map(prefix=".*/pipeline")

  return pipeline_handlers_map + [
      # Task queue handlers.
      (r".*/worker_callback", handlers.MapperWorkerCallbackHandler),
      (r".*/controller_callback", handlers.ControllerCallbackHandler),
      (r".*/kickoffjob_callback", handlers.KickOffJobHandler),
      (r".*/finalizejob_callback", handlers.FinalizeJobHandler),
      
#      (r".*/reduce_tags", ReduceTags),

      # RPC requests with JSON responses
      # All JSON handlers should have /command/ prefix.
      (r".*/command/start_job", handlers.StartJobHandler),
      (r".*/command/cleanup_job", handlers.CleanUpJobHandler),
      (r".*/command/abort_job", handlers.AbortJobHandler),
      (r".*/command/list_configs", status.ListConfigsHandler),
      (r".*/command/list_jobs", status.ListJobsHandler),
      (r".*/command/get_job_detail", status.GetJobDetailHandler),

      # UI static files
      (STATIC_RE, status.ResourceHandler),

      # Redirect non-file URLs that do not end in status/detail to status page.
      (r".*", RedirectHandler),
      ]

#def create_application():
#  """Create new WSGIApplication and register all handlers.
#
#  Returns:
#    an instance of webapp.WSGIApplication with all mapreduce handlers
#    registered.
#  """
#  return webapp.WSGIApplication(create_handlers_map(),
#                                debug=True)


#APP = create_application()

app = webapp2.WSGIApplication(create_handlers_map(),
                                debug=True)

#def main():
#  util.run_wsgi_app(APP)
#
#
#if __name__ == "__main__":
#  main()
