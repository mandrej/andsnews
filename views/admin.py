from __future__ import division
from datetime import datetime, timedelta

from google.appengine.ext import ndb
from google.appengine.api import memcache
from webapp2_extras.appengine.users import login_required, admin_required

from mapreduce.base_handler import PipelineBase
from mapreduce.mapper_pipeline import MapperPipeline
from models import Photo, Entry, Counter, Cloud, KEYS
from views.entry import make_thumbnail
from handlers import BaseHandler, csrf_protected, xss_protected, Paginator
from config import filesizeformat, PHOTOS_PER_PAGE, ENTRIES_PER_PAGE


class Cache(BaseHandler):
    def get(self):
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
        data = {'photo_count': Photo.query().order(-Photo.date).count(),
                'entry_count': Entry.query().order(-Entry.date).count(),
                'stats': stats,
                'oldest': oldest,
                'hit_ratio': hit_ratio}
        self.render_template('admin/index.html', data)


class Photos(BaseHandler):
    @login_required
    @xss_protected
    def get(self, field=None, value=None):
        page = int(self.request.get('page', 1))
        query = Photo.query_for(field, value)
        paginator = Paginator(query, per_page=PHOTOS_PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1,
                'tags_cloud': Cloud('Photo_tags').get_list(),
                'author_cloud': Cloud('Photo_author').get_list(),
                'date_cloud': Cloud('Photo_date').get_list()}
        self.render_template('admin/photos.html', data)


class Entries(BaseHandler):
    @login_required
    @xss_protected
    def get(self, field=None, value=None):
        page = int(self.request.get('page', 1))
        query = Entry.query_for(field, value)
        paginator = Paginator(query, per_page=ENTRIES_PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1,
                'tags_cloud': Cloud('Entry_tags').get_list(),
                'author_cloud': Cloud('Entry_author').get_list(),
                'date_cloud': Cloud('Entry_date').get_list()}
        self.render_template('admin/entries.html', data)

    @csrf_protected
    def post(self):
        params = dict(self.request.POST)
        key = ndb.Key(urlsafe=params['safe_key'])
        if params['action'] == 'delete':
            obj = key.get()
            obj.small = None
            obj.put()
            data = {'success': True}
        elif params['action'] == 'make':
            buff, mime = make_thumbnail('Entry', key.string_id(), 'small')
            data = {'success': True, 'small': filesizeformat(len(buff))}
        self.render_json(data)


class Counters(BaseHandler):
    """
    filter:
    /forkind/Photo/, /field/date/, /value/2010/
    """
    @admin_required
    @xss_protected
    def get(self, field=None, value=None):
        page = int(self.request.get('page', 1))
        query = Counter.query_for(field, value)
        paginator = Paginator(query, per_page=20)
        objects, has_next = paginator.page(page)
        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('admin/counters.html', data)

    @csrf_protected
    def post(self, page=1):
        # cntx = ndb.get_context()
        # cntx.set_cache_policy(False)
        page = int(page)
        if self.request.get('action:delete'):
            key = ndb.Key(urlsafe=self.request.get('action:delete'))
            key.delete()
        elif self.request.get('action:edit'):
            input_id = self.request.get('action:edit')
            key = ndb.Key(urlsafe=input_id)
            obj = key.get()
            obj.count = int(self.request.get('count.%s' % input_id))
            obj.put()
        self.redirect_to('counter_admin', page=page)


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
    "palette": {
        "job_name": "calculate_palette",
        "handler_spec": "views.background.calculate_palette",
        "input_reader_spec": "mapreduce.input_readers.DatastoreInputReader",
        "params": {
            "entity_kind": "models.Photo",
        },
        "shards": 4
    },
    "dimension": {
        "job_name": "calculate_dimension",
        "handler_spec": "views.background.calculate_dimension",
        "input_reader_spec": "mapreduce.input_readers.DatastoreInputReader",
        "params": {
            "entity_kind": "models.Photo",
        },
        "shards": 4
    }
}


class DatastoreMapperPipeline(PipelineBase):
    def run(self, job_name):
        yield MapperPipeline(**JOBS[job_name])


class DatastoreBackground(BaseHandler):
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
