import os
import re
import json
import uuid
import logging
import webapp2
import datetime
import cloudstorage as gcs
from operator import itemgetter
from PIL import Image
from cStringIO import StringIO
from google.appengine.api import users, memcache, app_identity
from google.appengine.ext import ndb, blobstore, deferred
from handlers import LazyEncoder, Paginator, SearchPaginator
from models import Cloud, Entry, Photo, get_exif, rgb_hls, range_names, incr_count, decr_count, update_tags, rounding, PHOTO_FIELDS
from palette import extract_colors
from config import TIMEOUT

LIMIT = 12
BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())


class RestHandler(webapp2.RequestHandler):
    def render(self, data):
        self.response.content_type = 'application/json; charset=utf-8'
        # self.response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
        self.response.write(json.dumps(data, cls=LazyEncoder))


class Collection(RestHandler):
    def get(self, kind=None, field=None, value=None):
        page = self.request.get('page', None)
        model = ndb.Model._kind_map.get(kind.title())
        query = model.query_for(field, value)
        paginator = Paginator(query, per_page=LIMIT)
        objects, token = paginator.page(page)

        if not objects:
            self.abort(404)

        self.render({
            'objects': objects,
            'filter': {'field': field, 'value': value} if (field and value) else None,
            'page': page,
            'next': token
        })


class Record(RestHandler):
    def get(self, kind=None, safe_key=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)

        self.render(obj)


def cloud_limit(items):
    """
    Returns limit for the specific count. Show only if count > limit
    :param items: dict {Photo_tags: 10, _date: 119, _eqv: 140, _iso: 94, _author: 66, _lens: 23, _model: 18, _color: 73
    :return: int
    """
    _curr = 0
    _sum5 = sum((x['count'] for x in items)) * 0.05
    if _sum5 < 1:
        return 0
    else:
        _on_count = sorted(items, key=itemgetter('count'))
        for item in _on_count:
            _curr += item['count']
            if _curr >= _sum5:
                return item['count']


def cloud_representation(kind):
    model = ndb.Model._kind_map.get(kind.title())
    data = memcache.get('%s_representation' % kind)

    if data is None:
        if kind == 'photo':
            fields = ['date', 'tags', 'model']
        elif kind == 'entry':
            fields = ['date', 'tags', 'author']

        data = []
        for field in fields:
            mem_key = kind.title() + '_' + field
            cloud = Cloud(mem_key).get_list()

            limit = cloud_limit(cloud)
            items = [x for x in cloud if x['count'] > limit]

            if field in ('tags', 'author', 'model', 'lens', 'iso',):
                items = sorted(items, key=itemgetter('count'), reverse=True)

            if field == 'date':
                items = sorted(items, key=itemgetter('name'), reverse=True)
            elif field in ('tags', 'author', 'model', 'lens', 'iso',):
                items = sorted(items, key=itemgetter('name'), reverse=False)
            elif field == 'color':
                items = sorted(items, key=itemgetter('order'))

            for item in items:
                query = model.query_for(field, item['name'])
                res = query.fetch(1)
                try:
                    obj = res[0]
                except IndexError:
                    pass
                else:
                    if kind == 'photo':
                        item['repr_url'] = obj.serving_url + '=s400'
                    elif kind == 'entry' and obj.front != -1:
                        item['repr_url'] = obj.image_url(obj.front)

            data.append({
                'field_name': field,
                'items': items
            })
        memcache.set('%s_representation' % kind, data, TIMEOUT * 2)

    return data


class KindFilter(RestHandler):  # from handlers.RenderCloud
    def get(self, kind=None):
        data = cloud_representation(kind)
        self.render(data)


class Find(RestHandler):
    def get(self, find):
        page = self.request.get('page', None)
        paginator = SearchPaginator(find, per_page=LIMIT)
        objects, number_found, token, error = paginator.page(page)

        self.render({
            'objects': objects,
            'phrase': find.strip(),
            'number_found': number_found,
            'page': page,
            'next': token,
            'error': error
        })


class EntryForm(RestHandler):
    def put(self, kind=None, safe_key=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        data = dict(self.request.params)
        logging.error(data)


class PhotoForm(RestHandler):
    def post(self):
        data = dict(self.request.params)  # {'file': FieldStorage('file', u'SDIM4151.jpg')}
        fs = data['file']
        if fs.done < 0:
            self.render({'success': False, 'message': 'Upload interrupted'})

        _buffer = fs.value
        object_name = BUCKET + '/' + fs.filename  # format /bucket/object
        # Check  GCS stat exist first
        try:
            gcs.stat(object_name)
            object_name = BUCKET + '/' + re.sub(r'\.', '-%s.' % str(uuid.uuid4())[:8], fs.filename)
        except gcs.NotFoundError:
            pass

        # Write to GCS
        try:
            write_retry_params = gcs.RetryParams(backoff_factor=1.1)
            with gcs.open(object_name, 'w', content_type=fs.type, retry_params=write_retry_params) as f:
                f.write(_buffer)  # <class 'cloudstorage.storage_api.StreamingBuffer'>
            # <class 'google.appengine.api.datastore_types.BlobKey'> or None
            blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + object_name))
            size = f.tell()
        except gcs.errors, e:
            self.render({'success': False, 'message':  e.message})
        else:
            obj = Photo(headline=fs.filename, blob_key=blob_key, filename=object_name, size=size)

            # Read EXIF
            exif = get_exif(_buffer)
            for field, value in exif.items():
                setattr(obj, field, value)

            # Set dim
            image_from_buffer = Image.open(StringIO(_buffer))
            obj.dim = image_from_buffer.size

            # Calculate Pallette
            image_from_buffer.thumbnail((100, 100), Image.ANTIALIAS)
            palette = extract_colors(image_from_buffer)
            if palette.bgcolor:
                colors = [palette.bgcolor] + palette.colors
            else:
                colors = palette.colors

            _max = 0
            for c in colors:
                h, l, s = rgb_hls(c.value)
                criteria = s * c.prominence
                if criteria >= _max:  # saturation could be 0
                    _max = criteria
                    obj.rgb = c.value
            obj.hue, obj.lum, obj.sat = range_names(obj.rgb)

            # SAVE EVERYTHING
            obj.put()

            incr_count(Photo, 'author', obj.author.nickname())
            incr_count(Photo, 'date', obj.year)
            for field in PHOTO_FIELDS:
                value = getattr(obj, field, None)
                if value:
                    incr_count(Photo, field, value)
            deferred.defer(obj.index_doc)

            self.render({'success': True, 'safe_key':  obj.key.urlsafe()})

    def put(self, kind=None, safe_key=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        data = dict(self.request.params)
        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        logging.error(data)
        obj.edit(data)


class Download(webapp2.RequestHandler):
    def get(self, safe_key):
        key = ndb.Key(urlsafe=safe_key)
        obj = key.get()
        buff = obj.buffer
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s.jpg' % key.string_id()
        self.response.write(buff)
