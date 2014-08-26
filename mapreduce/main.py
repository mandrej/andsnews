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





# Pipeline has to be imported before webapp.
try:
  from mapreduce.lib import pipeline
except ImportError:
  pipeline = None

# pylint: disable=g-import-not-at-top
# from google.appengine.ext import webapp
import webapp2
from mapreduce import handlers
from mapreduce import status
# from google.appengine.ext.webapp import util


STATIC_RE = r".*/([^/]*\.(?:css|js)|status|detail)$"

###################################################### mda 
from mapreduce import operation as op
from mapreduce import control
from mapreduce.model import MapreduceState
from google.appengine.ext import ndb, blobstore
from models import update_doc, rounding
from config import CROPS, ASA, LENGTHS
import itertools
import logging


def indexer(entity):
    update_doc(**entity.index_data)


def fixer(entity):
    logging.info(entity.headline)

    if entity.focal_length and entity.crop_factor:
        value = int(entity.focal_length * entity.crop_factor)
        entity.eqv = rounding(value, LENGTHS)
    if entity.iso:
        value = int(entity.iso)
        entity.iso = rounding(value, ASA)

    entity.put()

# def fixer(oldkey):
    # entity is oldkey for DatastoreKeyInputReader <class 'google.appengine.api.datastore_types.Key'>
    # key = ndb.Key.from_old_key(oldkey)  # <class 'google.appengine.ext.ndb.key.Key'>
    # key.delete()
    # obj = key.get()
    # buf = blobstore.BlobReader(obj.blob_key).read()
    # palette = img_palette(buf)
    #
    # obj.rgb = palette.colors[0].value
    # obj.hue, obj.lum, obj.sat = range_names(obj.rgb)

    # blob_info = blobstore.BlobInfo.get(obj.blob_key)
    # blob_reader = blob_info.open()
    # buff = blob_reader.read()
    #
    # file_name = files.blobstore.create(mime_type='image/jpeg',
    #     _blobinfo_uploaded_filename='%s.jpg' % obj.key.string_id())
    # with files.open(file_name, 'a') as f:
    #     f.write(buff)
    # files.finalize(file_name)
    #
    # obj.blob_key = files.blobstore.get_blob_key(file_name)
    # if hasattr(obj, 'rating'):
    #     delattr(obj, 'rating')
    # obj.put()

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

def create_application():
  """Create new WSGIApplication and register all handlers.

  Returns:
    an instance of webapp.WSGIApplication with all mapreduce handlers
    registered.
  """
  return webapp2.WSGIApplication(create_handlers_map(),
                                debug=True)


APP = create_application()


# def main():
#   util.run_wsgi_app(APP)
#
#
# if __name__ == "__main__":
#   main()
