import datetime
import re
import uuid
import logging
from cStringIO import StringIO

import cloudstorage as gcs
from PIL import Image
from google.appengine.api import images
from google.appengine.ext import ndb, deferred, blobstore

from config import BUCKET, PHOTO_FILTER
from helpers import slugify, tokenize, get_exif
from werkzeug.utils import cached_property


def filter_param(field, value):
    try:
        assert field and value
    except AssertionError:
        return {}

    if field == 'iso':
        value = int(value)

    return {field: value}


class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.GenericProperty(required=True)
    count = ndb.IntegerProperty(default=0)
    repr_stamp = ndb.DateTimeProperty()
    repr_url = ndb.StringProperty()

    @classmethod
    def all_photo_filter(cls):
        tmp = {}
        for field in PHOTO_FILTER:
            query = cls.query(cls.forkind == 'Photo', Counter.field == field)
            tmp[field] = [counter for counter in query if counter.count > 0]
        return tmp


class Photo(ndb.Model):
    headline = ndb.StringProperty(required=True)
    slug = ndb.ComputedProperty(lambda self: slugify(self.headline))
    email = ndb.StringProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    blob_key = ndb.BlobKeyProperty()
    filename = ndb.StringProperty()  # /bucket/object

    size = ndb.IntegerProperty()
    dim = ndb.IntegerProperty(repeated=True)  # width, height
    model = ndb.StringProperty()
    lens = ndb.StringProperty()
    aperture = ndb.FloatProperty()
    shutter = ndb.StringProperty()
    focal_length = ndb.FloatProperty()
    iso = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()

    year = ndb.ComputedProperty(lambda self: self.date.year)
    month = ndb.ComputedProperty(lambda self: self.date.month)
    nick = ndb.ComputedProperty(lambda self: re.match('([^@]+)', self.email).group().split('.')[0])
    text = ndb.ComputedProperty(lambda self: tokenize(self.slug), repeated=True)

    def update_filters(self, new_pairs, old_pairs):
        futures = []
        for field, value in set(new_pairs) | set(old_pairs):
            futures.append(self.query_for(field, value).get_async())

        counters = []
        for i, (field, value) in enumerate(set(new_pairs) | set(old_pairs)):
            key_name = 'Photo||{}||{}'.format(field, value)
            counter = Counter.get_or_insert(key_name, forkind='Photo', field=field, value=value)

            if (field, value) in old_pairs:
                counter.count -= 1
            if (field, value) in new_pairs:
                counter.count += 1
            counters.append(counter)

            latest = futures[i].get_result()
            if latest:
                counter.repr_stamp = latest.date
                counter.repr_url = latest.serving_url

        ndb.put_multi(counters)

    def changed_pairs(self):
        """
        List of changed field, value pairs
        [('year', 2017), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        """
        pairs = []
        for field in PHOTO_FILTER:
            value = getattr(self, field, None)
            if value:
                if isinstance(value, (list, tuple)):
                    for v in value:
                        pairs.append((field, str(v)))
                elif isinstance(value, int):
                    pairs.append((field, value))
                else:
                    pairs.append((field, str(value)))  # stringify year
        return pairs

    @property
    def buffer(self):
        """ Used for Download """
        contents = ''
        with gcs.open(self.filename, 'r') as f:
            contents = f.read()
        return contents

    def add(self, fs):
        """
        werkzeug.datastructures.FileStorage(stream=None, filename=None, name=None, content_type=None, content_length=None, headers=None)
        """
        _buffer = fs.stream.getvalue()
        # Check GCS stat exist first
        object_name = BUCKET + '/' + fs.filename  # format /bucket/object
        try:
            gcs.stat(object_name)
            object_name = BUCKET + '/' + re.sub(r'\.', '-%s.' % str(uuid.uuid4())[:8], fs.filename)
        except gcs.NotFoundError:
            pass

        # Write to GCS
        try:
            with gcs.open(object_name, 'w', content_type=fs.content_type) as f:
                f.write(_buffer)  # <class 'cloudstorage.storage_api.StreamingBuffer'>
            # <class 'google.appengine.api.datastore_types.BlobKey'> or None
            self.blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + object_name))
            self.filename = object_name
            self.size = f.tell()
        except gcs.errors as e:
            return {'success': False, 'message': e.message}
        else:
            # Read EXIF
            exif = get_exif(_buffer)
            for field, value in exif.items():
                setattr(self, field, value)

            # SAVE EVERYTHING
            image_from_buffer = Image.open(StringIO(_buffer))
            self.dim = image_from_buffer.size
            self.tags = ['new']  # ARTIFICIAL TAG
            self.put()

            new_pairs = self.changed_pairs()
            deferred.defer(self.update_filters, new_pairs, [], _queue='background')

            obj = self.serialize()
            if obj:
                return {'success': True, 'rec': obj}
            else:
                # remove file and record
                try:
                    gcs.delete(self.filename)
                except gcs.NotFoundError:
                    pass

                old_pairs = self.changed_pairs()
                deferred.defer(self.update_filters, [], old_pairs, _queue='background')
                self.key.delete()

                return {'success': False, 'message': 'Something went wrong. Picture not uploaded'}

    def edit(self, json):
        old_pairs = self.changed_pairs()

        # fix empty values
        values = map(lambda x: x if x != '' else None, json.values())
        json = dict(zip(json.keys(), values))

        self.headline = json['headline']
        self.email = json['email']
        self.model = json['model']
        self.shutter = json['shutter']
        self.lens = json['lens']

        # fix tags
        if 'tags' in json:
            tags = json['tags']
        else:
            tags = []
        self.tags = sorted(tags)

        # fix date no millis
        dt = json['date'].strip().split('.')[0]
        self.date = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')

        if json['focal_length']:
            self.focal_length = round(float(json['focal_length']), 1)
        if json['aperture']:
            self.aperture = float(json['aperture'])
        if json['iso']:
            self.iso = int(json['iso'])

        self.put()

        new_pairs = self.changed_pairs()
        deferred.defer(self.update_filters, new_pairs, old_pairs, _queue='background')

        obj = self.serialize()
        if obj:
            return {'success': True, 'rec': obj}
        else:
            return {'success': False, 'message': 'Something went wrong'}

    def remove(self):
        old_pairs = self.changed_pairs()

        images.delete_serving_url(self.blob_key)
        try:
            gcs.delete(self.filename)
        except gcs.NotFoundError:
            pass

        deferred.defer(self.update_filters, [], old_pairs, _queue='background')
        self.key.delete()
        return {'success': True}

    @cached_property
    def serving_url(self):
        result = None
        try:
            result = images.get_serving_url(self.blob_key, crop=False, secure_url=True)
        except images.TransformationError:
            logging.error('__NO_IMAGE__,{},{}'.format(self.date.isoformat(), self.slug))

        return result

    @classmethod
    def query_for(cls, field, value):
        """[FilterNode('color', '=', 'pink')]"""
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)

    @classmethod
    def latest_for(cls, field, value):
        query = cls.query_for(field, value)
        return query.get()

    def serialize(self):
        if self.serving_url:
            data = self.to_dict(exclude=('blob_key', 'size', 'year', 'month', 'text'))
            data.update({
                'kind': 'photo',
                'safekey': self.key.urlsafe(),
                'serving_url': self.serving_url
            })
            return data
        return None
