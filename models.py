from __future__ import division

import re
import colorsys
import datetime
import logging
import base64
import uuid
from cStringIO import StringIO
from decimal import *

import webapp2
from PIL import Image
from google.appengine.api import users, search, images
from google.appengine.ext import ndb, deferred, blobstore

import cloudstorage as gcs
from operator import itemgetter
from config import COLORS, ASA, HUE, LUM, SAT, BUCKET
from exifread import process_file
from palette import extract_colors, rgb_to_hex
from slugify import slugify

logging.getLogger("exifread").setLevel(logging.WARNING)

TIMEOUT = 60  # 1 minute
INDEX = search.Index(name='searchindex')
PHOTO_FILTER_FIELDS = ('date', 'tags', 'model', 'color')
PHOTO_EXIF_FIELDS = ('model', 'lens', 'date', 'aperture', 'shutter', 'focal_length', 'iso')
PHOTO_COUNTER_FIELDS = ('date', 'tags', 'author', 'model', 'lens', 'color')
ENTRY_COUNTER_FIELDS = ('date', 'tags', 'author')


def rounding(val, values):
    return min(values, key=lambda x: abs(x - val))


def filter_param(field, value):
    try:
        assert (field and value)
    except AssertionError:
        return {}
    if field == 'date':
        field = 'year'
    elif field == 'author':
        value = users.User(email=value)
    try:
        value = int(value)
    except (ValueError, TypeError):
        pass
    return {field: value}


def get_exif(buff):
    """
    tags(details=False):

    'EXIF ApertureValue': (0x9202) Ratio=209759/62500 @ 544,
    'EXIF DateTimeDigitized': (0x9004) ASCII=2015:09:13 07:48:59 @ 516,
        'EXIF DateTimeOriginal': (0x9003) ASCII=2015:09:07 12:19:18 @ 496,
    'EXIF ExifVersion': (0x9000) Undefined=0230 @ 268,
    'EXIF ExposureBiasValue': (0x9204) Signed Ratio=-3/10 @ 552,
    'EXIF ExposureMode': (0xA402) Short=Manual Exposure @ 424,
    'EXIF ExposureProgram': (0x8822) Short=Program Normal @ 244,
        'EXIF ExposureTime': (0x829A) Ratio=1/80 @ 480,
    'EXIF Flash': (0x9209) Short=Flash did not fire @ 364,
        'EXIF FNumber': (0x829D) Ratio=16/5 @ 488,
        'EXIF FocalLength': (0x920A) Ratio=30 @ 568,
        'EXIF FocalLengthIn35mmFilm': (0xA405) Short=45 @ 448,
    'EXIF ImageUniqueID': (0xA420) ASCII=3030383036373531808E045635363034 @ 576,
        'EXIF ISOSpeedRatings': (0x8827) Short=100 @ 256,
    'EXIF MaxApertureValue': (0x9205) Ratio=97347/32767 @ 560,
    'EXIF MeteringMode': (0x9207) Short=CenterWeightedAverage @ 352,
    'EXIF SceneCaptureType': (0xA406) Short=Standard @ 460,
    'EXIF SensingMethod': (0xA217) Short=One-chip color area @ 388,
    'EXIF ShutterSpeedValue': (0x9201) Signed Ratio=790241/125000 @ 536,
    'EXIF WhiteBalance': (0xA403) Short=Auto @ 436,
    'Image DateTime': (0x0132) ASCII=2015:09:13 21:17:31 @ 190,
    'Image ExifOffset': (0x8769) Long=210 @ 102,
        'Image Make': (0x010F) ASCII=SIGMA @ 110,
        'Image Model': (0x0110) ASCII=SIGMA dp2 Quattro @ 116,
    'Image ResolutionUnit': (0x0128) Short=Pixels/Inch @ 66,
    'Image XResolution': (0x011A) Ratio=240 @ 134,
    'Image YResolution': (0x011B) Ratio=240 @ 142,
    'Thumbnail Compression': (0x0103) Short=JPEG (old-style) @ 620,
    'Thumbnail JPEGInterchangeFormat': (0x0201) Long=704 @ 668,
    'Thumbnail JPEGInterchangeFormatLength': (0x0202) Long=9699 @ 680,
    'Thumbnail ResolutionUnit': (0x0128) Short=Pixels/Inch @ 656,
    'Thumbnail XResolution': (0x011A) Ratio=72 @ 688,
    'Thumbnail YResolution': (0x011B) Ratio=72 @ 696
    """
    data = {}
    model = None
    make = None
    tags = process_file(StringIO(buff), details=False)

    if 'Image Model' in tags:
        model = tags['Image Model'].printable.replace('/', '')

    if 'Image Make' in tags:
        make = tags['Image Make'].printable.replace('/', '')

    if model and make:
        s1 = set(make.split())
        s2 = set(model.split())
        if s1 & s2:  # contain word in make and model
            data['model'] = model
        else:
            data['model'] = '%s %s' % (make, model)

    if 'EXIF LensModel' in tags:
        data['lens'] = tags['EXIF LensModel'].printable.replace('/', '')

    if 'EXIF DateTimeOriginal' in tags:
        data['date'] = datetime.datetime.strptime(tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
    else:
        data['date'] = datetime.datetime.now()

    if 'EXIF FNumber' in tags:
        getcontext().prec = 2
        data['aperture'] = float(Decimal(eval(tags['EXIF FNumber'].printable)))

    if 'EXIF ExposureTime' in tags:
        data['shutter'] = tags['EXIF ExposureTime'].printable

    if 'EXIF FocalLength' in tags:
        getcontext().prec = 2
        data['focal_length'] = float(Decimal(eval(tags['EXIF FocalLength'].printable)))

    if 'EXIF ISOSpeedRatings' in tags:
        getcontext().prec = 2
        value = int(Decimal(tags['EXIF ISOSpeedRatings'].printable) / 1)
        data['iso'] = rounding(value, ASA)

    # if 'GPS GPSLatitude' in tags:
    # deg_min_sec = eval(tags['GPS GPSLatitude'].printable)  # [44, 47, 559597/10000]
    # data['latitude'] = sum(map(divide60, enumerate(deg_min_sec)))  # [(0, 44), (1, 47), (2, 55.9597)]

    # if 'GPS GPSLongitude' in tags:
    #     d, m, s = eval(tags['GPS GPSLongitude'].printable)  # [20, 28, 508547/10000]
    #     data['longitude'] = d + m / 60 + s / 3600

    return data


def rgb_hls(rgb):
    def intround(n):
        return int(round(n))

    rel_rgb = map(lambda x: x/255.0, rgb)
    h, l, s = colorsys.rgb_to_hls(*rel_rgb)
    return map(intround, (h*360, l*100, s*100))


def range_names(rgb):
    def in_range(value, component):
        match = next((x for x in component if value in x['span']), None)
        if match:
            return match['name']
        return 'none'

    h, l, s = rgb_hls(rgb)
    hue = in_range(h % 360, HUE)
    lum = in_range(l, LUM)
    sat = in_range(s, SAT)
    return hue, lum, sat


def tokenize(phrase):
    res = []
    for word in phrase.split('-'):
        for i in range(3, len(word) + 1):
            res.append(word[:i])
    return ' '.join(res)


def remove_doc(safe_key):
    INDEX.delete(safe_key)


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


def sorting_filters(kind, fields):
    data = []
    for field in fields:
        mem_key = kind.title() + '_' + field
        cloud = Cloud(mem_key).get_list()
        # [{'count': 1, 'name': 'montenegro', 'repr_url': '...'}, ...]

        limit = cloud_limit(cloud)
        items = [x for x in cloud if x['count'] > limit]

        if field == 'date':
            items = sorted(items, key=itemgetter('name'), reverse=True)
        elif field in ('tags', 'author', 'model', 'lens', 'iso'):
            items = sorted(items, key=itemgetter('name'), reverse=False)
        elif field == 'color':
            items = sorted(items, key=itemgetter('order'))
            map(lambda d: d.pop('order'), items)

        data.append({
            'field_name': field,
            'items': items
        })

    return data


class Cloud(object):
    """ cache dictionary collections on unique values and it's counts
        {'still life': {'count': 8, 'repr_url': '...'}, ...}

        get_list:
        [{'count': 1, 'name': 'montenegro', 'repr_url': '...'}, ...]
    """

    def __init__(self, mem_key):
        self.mem_key = mem_key
        self.kind, self.field = mem_key.split('_', 1)

    def get(self):
        return self.make()

    def get_list(self):
        collection = self.get()

        content = []
        if self.field == 'color':
            for k, d in collection.items():
                data = next(({'name': x['name'], 'order': x['order']} for x in COLORS if x['name'] == k), None)
                data.update({'count': d['count'], 'repr_url': d['repr_url']})
                content.append(data)
        else:
            for k, d in collection.items():
                data = {'name': k, 'count': d['count'], 'repr_url': d['repr_url']}
                content.append(data)

        return content

    def make(self):
        collection = {}
        query = Counter.query(Counter.forkind == self.kind, Counter.field == self.field)
        for counter in query:
            if counter.count > 0:
                collection[counter.value] = {'count': counter.count, 'repr_url': counter.repr_url}
        # {'still life': {'count': 8, 'repr_url': '...'}, ...}
        return collection


# class Graph(object):
#     def __init__(self, field):
#         self.field = field
#         self.mem_key = '%s_graph' % field
#
#     def get_json(self):
#         collection = memcache.get(self.mem_key)
#         if collection is None:
#             query = Photo.query(getattr(Photo, self.field).IN(['milan', 'svetlana', 'ana', 'mihailo', 'milos',
#                                                                'katarina', 'iva', 'masa', 'djordje']))
#             res = [x.tags for x in query]
#             flat = reduce(lambda x, y: x + y, res)
#
#             tally = {}
#             for name in flat:
#                 if name in tally:
#                     tally[name] += 1
#                 else:
#                     tally[name] = 1
#
#             i = 0
#             nodes = []
#             items = {}
#             for name, count in tally.items():
#                 items[name] = i
#                 nodes.append({'name': name, 'index': i, 'count': count})
#                 i += 1
#
#             links = []
#             pairs = itertools.combinations(items.keys(), 2)
#             for x, y in pairs:
#                 i = 0
#                 for tags in res:
#                     intersection = set(tags) & {x, y}  # set literals back-ported from Python 3.x
#                     i += intersection == {x, y}
#                 if i > 0:
#                     links.append({'source': items[x], 'target': items[y], 'value': i})
#
#             collection = {'nodes': nodes, 'links': links}
#             memcache.set(self.mem_key, collection, TIMEOUT * 12)
#
#         return collection


class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.GenericProperty(required=True)  # stringify year StringProperty
    count = ndb.IntegerProperty(default=0)
    repr_stamp = ndb.DateTimeProperty()
    repr_url = ndb.StringProperty()


def update_counter(delta, args):
    try:
        assert len(args) == 3
    except AssertionError:
        logging.error(args)
    else:
        key_name = '%s||%s||%s' % args
        params = dict(zip(('forkind', 'field', 'value'), map(str, args)))  # stringify year

        obj = Counter.get_or_insert(key_name, **params)
        obj.count += delta
        obj.put()


@ndb.toplevel
def update_representation(new_pairs, old_pairs):
    # PHOTO ONLY
    queries = []
    key_names = []
    params = []
    for field, value in set(new_pairs) | set(old_pairs):  # union
        queries.append(Photo.query_for(field, value))
        args = ('Photo', field, str(value))  # stringify year
        key_names.append('%s||%s||%s' % args)
        params.append(dict(zip(('forkind', 'field', 'value'), args)))

    for i, query in enumerate(queries):
        latest = query.get()
        counter = Counter.get_or_insert(key_names[i], **params[i])

        if latest is not None and latest.date != counter.repr_stamp:
            counter.repr_stamp = latest.date
            counter.repr_url = latest.serving_url
            counter.put_async()
            logging.info('UPDATE %s %s' % (key_names[i], counter.count))


def incr_count(*args):
    deferred.defer(update_counter, 1, args)


def decr_count(*args):
    deferred.defer(update_counter, -1, args)


def update_counter_field(old, new, kind, field):
    if field == 'tags':
        old_tags = set(old or [])
        new_tags = set(new or [])
        if old_tags - new_tags:
            for name in list(old_tags - new_tags):
                decr_count(kind, field, name)
        if new_tags - old_tags:
            for name in list(new_tags - old_tags):
                incr_count(kind, field, name)
    else:
        if old != new:
            if old:
                if field == 'author':
                    decr_count(kind, field, old.email())
                elif field == 'date':
                    decr_count(kind, field, old.year)
                else:
                    decr_count(kind, field, old)
            if new:
                if field == 'author':
                    incr_count(kind, field, new.email())
                elif field == 'date':
                    incr_count(kind, field, new.year)
                else:
                    incr_count(kind, field, new)


class Photo(ndb.Model):
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty()
    tags = ndb.StringProperty(repeated=True)
    blob_key = ndb.BlobKeyProperty()
    size = ndb.IntegerProperty()
    # EXIF data
    model = ndb.StringProperty()
    aperture = ndb.FloatProperty()
    shutter = ndb.StringProperty()
    focal_length = ndb.FloatProperty()
    iso = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()
    year = ndb.ComputedProperty(lambda self: self.date.year)
    # added fields
    lens = ndb.StringProperty()
    # calculated
    # RGB [86, 102, 102]
    rgb = ndb.IntegerProperty(repeated=True)
    # HLS names
    hue = ndb.StringProperty()
    lum = ndb.StringProperty()
    sat = ndb.StringProperty()
    # image dimension
    dim = ndb.IntegerProperty(repeated=True)  # width, height
    filename = ndb.StringProperty()

    color = ndb.ComputedProperty(
        lambda self: self.lum if self.lum in ('dark', 'light',) or self.sat == 'monochrome' else self.hue)

    slug = ndb.ComputedProperty(lambda self: slugify(self.headline))

    def index_doc(self):
        doc = search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(name='slug', value=tokenize(self.slug)),
                search.TextField(name='author', value=' '.join(self.author.nickname().split('.'))),
                search.TextField(name='tags', value=' '.join(self.tags)),
                search.NumberField(name='year', value=self.year),
                search.NumberField(name='month', value=self.date.month)]
        )
        INDEX.put(doc)

    def changed_pairs(self):
        """
        List of changed field, value pairs
        [('date', '2016'), ('tags', 'b&w'), ('tags', 'still life'), ('model', 'SIGMA dp2 Quattro')]
        """
        pairs = []
        for field in PHOTO_FILTER_FIELDS:
            prop = field
            if field == 'date':
                prop = 'year'
            value = getattr(self, prop, None)
            if value:
                if isinstance(value, (list, tuple)):
                    for v in value:
                        pairs.append((field, str(v)))
                else:
                    pairs.append((field, str(value)))  # stringify year
        return pairs

    @webapp2.cached_property
    def buffer(self):
        blob_reader = blobstore.BlobReader(self.blob_key, buffer_size=1024*1024)
        return blob_reader.read(size=-1)

    @webapp2.cached_property
    def thumb64(self):
        _buffer = StringIO()
        im = Image.open(StringIO(self.buffer))
        im.thumbnail((50, 50), Image.ANTIALIAS)
        im.save(_buffer, format=im.format)
        return base64.b64encode(_buffer.getvalue())

    def add(self, fs):
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

            # Set dim
            image_from_buffer = Image.open(StringIO(_buffer))
            self.dim = image_from_buffer.size

            # Calculate Pallette
            image_from_buffer.thumbnail((100, 100), Image.NEAREST)
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
                    self.rgb = c.value
            self.hue, self.lum, self.sat = range_names(self.rgb)

            # SAVE EVERYTHING
            self.author = users.User(email='milan.andrejevic@gmail.com')  # FORCE FIELD
            self.tags = ['new']  # ARTIFICIAL TAG
            self.put()

            for field in PHOTO_COUNTER_FIELDS:
                value = getattr(self, field, None)
                update_counter_field(None, value, 'Photo', field)

            new_pairs = self.changed_pairs()
            deferred.defer(update_representation, new_pairs, [])
            return {'success': True, 'safe_key':  self.key.urlsafe()}

    def edit(self, data):
        old_pairs = self.changed_pairs()

        for field in PHOTO_COUNTER_FIELDS:
            value = getattr(self, field, None)
            update_counter_field(value, data[field], 'Photo', field)

        self.headline = data['headline']
        self.author = data['author']
        self.tags = data['tags']
        self.model = data['model']
        self.aperture = data['aperture']
        self.shutter = data['shutter']
        self.focal_length = data['focal_length']
        self.lens = data['lens']
        self.iso = data['iso']
        self.date = data['date']
        self.put()
        deferred.defer(self.index_doc)

        new_pairs = self.changed_pairs()
        deferred.defer(update_representation, new_pairs, old_pairs)

    def remove(self):
        deferred.defer(remove_doc, self.key.urlsafe())
        blobstore.delete(self.blob_key)

        for field in PHOTO_COUNTER_FIELDS:
            value = getattr(self, field, None)
            update_counter_field(value, None, 'Photo', field)

        old_pairs = self.changed_pairs()
        self.key.delete()
        deferred.defer(update_representation, [], old_pairs)

    @webapp2.cached_property
    def serving_url(self):
        return images.get_serving_url(self.blob_key, crop=False, secure_url=True)

    @webapp2.cached_property
    def download_url(self):
        return webapp2.uri_for('download_url', safe_key=self.key.urlsafe())

    @property
    def hex(self):
        return rgb_to_hex(tuple(self.rgb))

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
        data = self.to_dict(exclude=(
            'blob_key', 'size', 'ratio', 'crop_factor',
            'rgb', 'sat', 'lum', 'hue', 'year', 'filename'))
        data.update({
            'kind': 'photo',
            'year': str(self.year),
            'safekey': self.key.urlsafe(),
            'serving_url': self.serving_url,
            'thumb64': self.thumb64
        })
        return data


class Entry(ndb.Model):
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty()
    summary = ndb.StringProperty(required=True)
    body = ndb.TextProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty()
    year = ndb.ComputedProperty(lambda self: self.date.year)
    front_img = ndb.StringProperty()

    slug = ndb.ComputedProperty(lambda self: slugify(self.headline))

    def index_doc(self):
        doc = search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(name='slug', value=tokenize(self.slug)),
                search.TextField(name='author', value=' '.join(self.author.nickname().split('.'))),
                search.TextField(name='tags', value=' '.join(self.tags)),
                search.NumberField(name='year', value=self.year),
                search.NumberField(name='month', value=self.date.month),
                search.HtmlField(name='body', value=self.body)]
        )
        INDEX.put(doc)

    def add(self, data):
        self.headline = data['headline']
        self.author = data['author']
        self.summary = data['summary']
        self.body = data['body']
        self.tags = data['tags']
        self.date = data['date']
        self.front_img = data['front_img']
        self.put()

        for field in ENTRY_COUNTER_FIELDS:
            value = getattr(self, field, None)
            update_counter_field(None, value, 'Entry', field)

        deferred.defer(self.index_doc)

    def edit(self, data):
        for field in ENTRY_COUNTER_FIELDS:
            value = getattr(self, field, None)
            update_counter_field(value, data[field], 'Entry', field)

        self.headline = data['headline']
        self.author = data['author']
        self.summary = data['summary']
        self.body = data['body']
        self.tags = data['tags']
        self.date = data['date']
        self.front_img = data['front_img']
        self.put()

        deferred.defer(self.index_doc)

    def remove(self):
        deferred.defer(remove_doc, self.key.urlsafe())

        for field in ENTRY_COUNTER_FIELDS:
            value = getattr(self, field, None)
            update_counter_field(value, None, 'Entry', field)

        self.key.delete()

    @classmethod
    def query_for(cls, field, value):
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)

    @classmethod
    def latest_for(cls, field, value):
        query = cls.query_for(field, value)
        result = query.fetch(1)
        if result:
            return result[0]
        return None

    def serialize(self):
        data = self.to_dict(exclude=('front', 'year'))
        data.update({
            'kind': 'entry',
            'year': str(self.year),
            'safekey': self.key.urlsafe()
        })
        return data
