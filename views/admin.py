from __future__ import division
from datetime import datetime, timedelta

from google.appengine.ext import ndb
from google.appengine.api import memcache
from webapp2_extras.appengine.users import login_required, admin_required

from mapreduce.base_handler import PipelineBase
from mapreduce.mapper_pipeline import MapperPipeline
from models import Photo, Entry, Counter, Cloud, KEYS
from handlers import BaseHandler, csrf_protected, xss_protected


class Cache(BaseHandler):
    def get(self, mem_key=None):
        if mem_key is not None:
            data = memcache.get(mem_key)
        else:
            data = dict(zip(KEYS, [None] * len(KEYS)))
            data.update(memcache.get_multi(KEYS))

        self.render_json(data)

    def put(self, mem_key):
        cloud = Cloud(mem_key)
        cloud.rebuild()
        self.render_json(cloud.get_cache())

    def delete(self, mem_key):
        memcache.delete(mem_key)
        self.render_json(None)


class Index(BaseHandler):
    @login_required
    def get(self):
        stats = memcache.get_stats()
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        all = hits + misses

        delta = stats.get('oldest_item_age', 0)  # seconds
        weeks, rem1 = divmod(delta, 604800)
        days, rem2 = divmod(rem1, 86400)
        hours, rem3 = divmod(rem2, 3600)
        minutes, seconds = divmod(rem3, 60)
        oldest = datetime.now() - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

        try:
            hit_ratio = 100 * hits / all
        except ZeroDivisionError:
            hit_ratio = 0
        data = {'counter_count': Counter.query().count(),
                'stats': stats,
                'oldest': oldest,
                'hit_ratio': hit_ratio}
        self.render_template('admin/index.html', data)


class Counters(BaseHandler):
    """
    filter:
    /forkind/Photo/, /field/date/, /value/2010/
    """
    @admin_required
    @xss_protected
    def get(self, field=None, value=None):
        page = self.request.get('page', None)
        query = Counter.query_for(field, value)
        paginator = Paginator(query, per_page=20)
        objects, token = paginator.page(page)
        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'next': token}
        self.render_template('admin/counters.html', data)

    @csrf_protected
    def post(self):
        # cntx = ndb.get_context()
        # cntx.set_cache_policy(False)
        if self.request.get('action:delete'):
            key = ndb.Key(urlsafe=self.request.get('action:delete'))
            key.delete()
        elif self.request.get('action:edit'):
            input_id = self.request.get('action:edit')
            key = ndb.Key(urlsafe=input_id)
            obj = key.get()
            obj.count = int(self.request.get('count.%s' % input_id))
            obj.put()
        self.redirect_to('counter_admin')


JOBS = {
    "photo_index": {
        "job_name": "full_photo_index",
        "handler_spec": "views.background.indexer",
        "input_reader_spec": "mapreduce.input_readers.DatastoreInputReader",
        "params": {
            "entity_kind": "models.Photo",
        },
        "shards": 4
    },
    "entry_index": {
        "job_name": "full_entry_index",
        "handler_spec": "views.background.indexer",
        "input_reader_spec": "mapreduce.input_readers.DatastoreInputReader",
        "params": {
            "entity_kind": "models.Entry",
        },
        "shards": 4
    },
    "fix": {
        "job_name": "current_fix",
        "handler_spec": "views.background.current_fix",
        "input_reader_spec": "mapreduce.input_readers.DatastoreInputReader",
        "params": {
            "entity_kind": "models.Photo",
        },
        "shards": 4
    },
}


class DatastoreMapperPipeline(PipelineBase):
    def run(self, job_name):
        yield MapperPipeline(**JOBS[job_name])


class DatastoreBackground(BaseHandler):
    @admin_required
    def get(self, job):
        try:
            JOBS[job]
        except KeyError:
            self.abort(404)
        else:
            pipeline = DatastoreMapperPipeline(job)
            pipeline.start()
            redirect_url = "%s/status?root=%s" % (pipeline.base_path, pipeline.pipeline_id)
            self.redirect(redirect_url)
