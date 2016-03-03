from __future__ import division

import cgi
import collections
import colorsys
import datetime
import itertools
import logging
import math
from cStringIO import StringIO
from decimal import *

import webapp2
from PIL import Image
from google.appengine.api import users, memcache, search, images
from google.appengine.ext import ndb, deferred, blobstore
from webapp2_extras.i18n import lazy_gettext as _

import cloudstorage as gcs
from config import COLORS, ASA, LENGTHS, HUE, LUM, SAT, TIMEOUT, BUCKET
from exifread import process_file
from palette import extract_colors, rgb_to_hex

logging.getLogger("exifread").setLevel(logging.WARNING)

INDEX = search.Index(name='searchindex')
KEYS = ['Photo_tags', 'Photo_author', 'Photo_date',
        'Photo_model', 'Photo_lens', 'Photo_eqv', 'Photo_iso', 'Photo_color',
        'Entry_tags', 'Entry_author', 'Entry_date']
PHOTO_FIELDS = ('model', 'lens', 'eqv', 'iso', 'color',)
ENTRY_IMAGES = 10
LOGARITHMIC, LINEAR = 1, 2


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
        # TODO Not all emails are gmail
        value = users.User(email='%s@gmail.com' % value)
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

    if all(tag in tags for tag in ['EXIF FocalLengthIn35mmFilm', 'EXIF FocalLength']):
        data['crop_factor'] = round(
            float(Decimal(tags['EXIF FocalLengthIn35mmFilm'].printable)) / data['focal_length'], 1)

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


def _calculate_thresholds(min_weight, max_weight, steps):
    delta = (max_weight - min_weight) / steps
    return [min_weight + i * delta for i in range(1, steps + 1)]


def _calculate_tag_weight(weight, max_weight, distribution):
    if distribution == LINEAR or max_weight == 1:
        return weight
    elif distribution == LOGARITHMIC:
        return math.log(weight) * max_weight / math.log(max_weight)
    raise ValueError('Invalid distribution algorithm specified: %s.' % distribution)


def calculate_cloud(tags, steps=8, distribution=LOGARITHMIC):
    """
    tags:  {u'mihailo': 2L, u'urban': 2L, u'belgrade': 3L, u'macro': 5L, ...}
    return [{'count': 2L, 'name': u'mihailo', 'size': 1},
            {'count': 5L, 'name': u'macro', 'size': 7}, ...]
    """
    data = []
    if len(tags) > 0:
        counts = tags.values()
        min_weight = float(min(counts))
        max_weight = float(max(counts)) + 0.0000001
        thresholds = _calculate_thresholds(min_weight, max_weight, steps)
        for key, val in tags.items():
            font_set = False
            tag_weight = _calculate_tag_weight(val, max_weight, distribution)
            for i in range(steps):
                if not font_set and tag_weight <= thresholds[i]:
                    data.append({'name': key, 'count': val, 'size': i + 1})
                    font_set = True
                    break
    return data


class Cloud(object):
    """ cache dictionary collections on unique values and it's counts
        {u'mihailo': 5, u'milos': 1, u'iva': 8, u'belgrade': 2, u'urban': 1, u'macro': 1, u'wedding': 3, ...}

        get_list:
        [{'size': 4, 'count': 3, 'name': 'mihailo.genije'}, {'size': 8, 'count': 11, 'name': 'milan.andrejevic'}, ...]
    """

    def __init__(self, mem_key):
        self.mem_key = mem_key
        self.kind, self.field = mem_key.split('_', 1)

    def set_cache(self, collection):
        memcache.set(self.mem_key, collection, TIMEOUT * 2)

    def get_cache(self):
        return memcache.get(self.mem_key)

    def get_list(self):
        collection = self.get_cache() or self.make()
        # {'iva': 1, 'milan': 1, 'svetlana': 1, 'urban': 1, 'portrait': 2, 'djordje': 2, 'belgrade': 1}
        content = []
        if self.field == 'color':
            for k, count in collection.items():
                data = next((x for x in COLORS if x['name'] == k), None)
                data.update({'count': count, 'field': self.field})
                content.append(data)
        else:
            content = calculate_cloud(collection)
        return content

    def make(self):
        collection = {}
        query = Counter.query(Counter.forkind == self.kind, Counter.field == self.field)
        for counter in query:
            if counter.count > 0:
                collection[counter.value] = counter.count
        self.set_cache(collection)
        return collection

    @ndb.toplevel
    def update(self, key, delta):
        collection = self.get_cache()
        if collection is not None:
            if key in collection:
                collection[key] += delta
            else:
                collection[key] = delta
            if collection[key] > 0:
                self.set_cache(collection)
            else:
                entity_key = ndb.Key('Counter', '%s||%s||%s' % (self.kind, self.field, key))
                entity_key.delete_async()
                del collection[key]

    @ndb.toplevel
    def rebuild(self):
        prop = self.field
        if self.field == 'date':
            prop = 'year'
        model = ndb.Model._kind_map.get(self.kind)  # TODO REMEMBER THIS
        query = model.query()
        properties = (getattr(x, prop, None) for x in query)  # generator
        if prop == 'tags':
            properties = list(itertools.chain(*properties))
        elif prop == 'author':
            properties = [x.nickname() for x in properties]
        tally = collections.Counter(filter(None, properties))  # filter out None

        collection = dict(tally.items())
        self.set_cache(collection)

        # repair counters async with toplevel
        for value, count in collection.items():
            key_name = '%s||%s||%s' % (self.kind, self.field, value)
            params = dict(zip(('forkind', 'field', 'value'), [self.kind, self.field, value]))
            obj = Counter.get_or_insert(key_name, **params)
            if obj.count != count:
                obj.count = count
                obj.put_async()

        return collection


class Graph(object):
    def __init__(self, field):
        self.field = field
        self.mem_key = '%s_graph' % field

    def get_json(self):
        collection = memcache.get(self.mem_key)
        if collection is None:
            query = Photo.query(getattr(Photo, self.field).IN(['milan', 'svetlana', 'ana', 'mihailo', 'milos',
                                                               'katarina', 'iva', 'masa', 'djordje']))
            res = [x.tags for x in query]
            flat = reduce(lambda x, y: x + y, res)

            tally = {}
            for name in flat:
                if name in tally:
                    tally[name] += 1
                else:
                    tally[name] = 1

            i = 0
            nodes = []
            items = {}
            for name, count in tally.items():
                items[name] = i
                nodes.append({'name': name, 'index': i, 'count': count})
                i += 1

            links = []
            pairs = itertools.combinations(items.keys(), 2)
            for x, y in pairs:
                i = 0
                for tags in res:
                    intersection = set(tags) & {x, y}  # set literals back-ported from Python 3.x
                    i += intersection == {x, y}
                if i > 0:
                    links.append({'source': items[x], 'target': items[y], 'value': i})

            collection = {'nodes': nodes, 'links': links}
            memcache.set(self.mem_key, collection, TIMEOUT * 12)

        return collection


class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.GenericProperty(required=True)  # could be int as str
    count = ndb.IntegerProperty(default=0)

    @classmethod
    def query_for(cls, field, value):
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters)


def update_counter(delta, args):
    try:
        assert len(args) == 3
    except AssertionError:
        logging.error(args)
    else:
        key_name = '%s||%s||%s' % args
        params = dict(zip(('forkind', 'field', 'value'), args))

        obj = Counter.get_or_insert(key_name, **params)
        obj.count += delta
        obj.put()

        mem_key = '{forkind}_{field}'.format(**params)
        cloud = Cloud(mem_key)
        cloud.update(params['value'], delta)


def incr_count(*args):
    deferred.defer(update_counter, 1, args)


def decr_count(*args):
    deferred.defer(update_counter, -1, args)


def update_tags(kind, old, new):
    old_tags = set(old or [])
    new_tags = set(new or [])
    if old_tags - new_tags:
        for name in list(old_tags - new_tags):
            decr_count(kind, 'tags', name)
    if new_tags - old_tags:
        for name in list(new_tags - old_tags):
            incr_count(kind, 'tags', name)


class Photo(ndb.Model):
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty(auto_current_user_add=True)
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
    crop_factor = ndb.FloatProperty()
    # calculated
    eqv = ndb.IntegerProperty()
    # RGB [86, 102, 102]
    rgb = ndb.IntegerProperty(repeated=True)
    # HLS names
    hue = ndb.StringProperty()
    lum = ndb.StringProperty()
    sat = ndb.StringProperty()
    # image dimension
    dim = ndb.IntegerProperty(repeated=True)  # width, height
    filename = ndb.StringProperty()

    ratio = ndb.ComputedProperty(
        lambda self: self.dim[0] / self.dim[1] if self.dim and len(self.dim) == 2 else 1.5)

    color = ndb.ComputedProperty(
        lambda self: self.lum if self.lum in ('dark', 'light',) or self.sat == 'monochrome' else self.hue)

    @webapp2.cached_property
    def kind(self):
        return self.key.kind()

    def index_doc(self):
        doc = search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(name='slug', value=tokenize(self.key.string_id())),
                search.TextField(name='author', value=' '.join(self.author.nickname().split('.'))),
                search.TextField(name='tags', value=' '.join(self.tags)),
                search.NumberField(name='year', value=self.year),
                search.NumberField(name='month', value=self.date.month),
                search.TextField(name='model', value=self.model)]
        )
        INDEX.put(doc)

    @webapp2.cached_property
    def buffer(self):
        blob_reader = blobstore.BlobReader(self.blob_key, buffer_size=1024*1024)
        return blob_reader.read(size=-1)

    def add(self, data):
        fs = data['photo']  # FieldStorage('photo', u'SDIM4151.jpg')
        if fs.done < 0:
            return {'success': False, 'message': _('Upload interrupted')}

        # Write to GCS and get stat
        try:
            _buffer = fs.value
            object_name = BUCKET + '/' + fs.filename  # format /bucket/object
            write_retry_params = gcs.RetryParams(backoff_factor=1.1)
            with gcs.open(object_name, 'w', content_type=fs.type, retry_params=write_retry_params) as f:
                f.write(_buffer)  # <class 'cloudstorage.storage_api.StreamingBuffer'>
            # <class 'google.appengine.api.datastore_types.BlobKey'> or None
            self.blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + object_name))
            self.filename = object_name
            self.size = f.tell()
        except gcs.errors, e:
            return {'success': False, 'message': e.message}
        else:
            self.headline = data['headline']
            # TODO Not all emails are gmail
            self.author = users.User(email='%s@gmail.com' % data['author'])
            self.tags = data['tags']

            # Read EXIF
            exif = get_exif(_buffer)
            for field, value in exif.items():
                setattr(self, field, value)

            # Set dim
            image_from_buffer = Image.open(StringIO(_buffer))
            self.dim = image_from_buffer.size

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
                    self.rgb = c.value
            self.hue, self.lum, self.sat = range_names(self.rgb)

            # SAVE EVERYTHING
            self.put()

            incr_count(self.kind, 'author', self.author.nickname())
            incr_count(self.kind, 'date', self.year)
            update_tags(self.kind, None, self.tags)
            for field in PHOTO_FIELDS:
                value = getattr(self, field, None)
                if value:
                    incr_count(self.kind, field, value)
            deferred.defer(self.index_doc)
            return {'success': True}

    def edit(self, data):
        old = self.author.nickname()
        new = data['author']
        if new != old:
            # TODO Not all emails are gmail
            self.author = users.User(email='%s@gmail.com' % new)
            decr_count(self.kind, 'author', old)
            incr_count(self.kind, 'author', new)
        del data['author']

        old = self.date
        new = data['date']
        if old != new:
            decr_count(self.kind, 'date', self.year)
            incr_count(self.kind, 'date', new.year)
        else:
            del data['date']

        update_tags(self.kind, self.tags, data['tags'])
        self.tags = sorted(data['tags'])
        del data['tags']

        if data['focal_length']:
            old = self.focal_length
            new = round(data['focal_length'], 1)
            if old != new:
                self.focal_length = new
            del data['focal_length']
        if data['crop_factor']:
            old = self.crop_factor
            new = round(data['crop_factor'], 1)
            if old != new:
                self.crop_factor = new
            del data['crop_factor']
        if self.focal_length and self.crop_factor:
            value = int(self.focal_length * self.crop_factor)
            data['eqv'] = rounding(value, LENGTHS)

        for field, value in data.items():
            if field in PHOTO_FIELDS:
                old = getattr(self, field)
                new = data.get(field)
                if old != new:
                    if old:
                        decr_count(self.kind, field, old)
                    if new:
                        incr_count(self.kind, field, new)
                    setattr(self, field, new)
            else:
                setattr(self, field, value)

        self.put()

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        deferred.defer(remove_doc, key.urlsafe())
        blobstore.delete(obj.blob_key)

        decr_count(key.kind(), 'author', obj.author.nickname())
        decr_count(key.kind(), 'date', obj.year)
        update_tags(key.kind(), obj.tags, None)
        for field in PHOTO_FIELDS:
            value = getattr(obj, field)
            if value:
                decr_count(key.kind(), field, value)
        ndb.delete_multi([x.key for x in ndb.Query(ancestor=key) if x.key != key])

    @property
    def serving_url(self):
        return images.get_serving_url(self.blob_key, crop=False, secure_url=True)

    @webapp2.cached_property
    def hex(self):
        return rgb_to_hex(tuple(self.rgb))

    @webapp2.cached_property
    def hls(self):
        return rgb_hls(self.rgb)

    @classmethod
    def query_for(cls, field, value):
        """[FilterNode('color', '=', 'pink')]"""
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)

    @classmethod
    def latest(cls):
        query = cls.query().order(-cls.date)
        result = query.fetch(1)
        if result:
            return result[0]
        return None

    def serialize(self):
        data = self.to_dict(exclude=(
            'blob_key', 'dim', 'size', 'ratio',
            'rgb', 'sat', 'lum', 'hue', 'year',
            'aperture', 'shutter', 'focal_length', 'crop_factor'))
        data.update({
            'slug': self.key.string_id(),
            'url': webapp2.uri_for('photo', slug=self.key.string_id()),
            'serving_url': self.serving_url,
        })
        return data


class Img(ndb.Model):
    # parent Entry
    name = ndb.StringProperty()
    num = ndb.IntegerProperty(default=0)
    blob = ndb.BlobProperty(default=None)
    small = ndb.BlobProperty(default=None)
    mime = ndb.StringProperty(default='image/jpeg')


class Entry(ndb.Model):
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty(auto_current_user_add=True)
    summary = ndb.StringProperty(required=True)
    body = ndb.TextProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty()
    year = ndb.ComputedProperty(lambda self: self.date.year)
    front = ndb.IntegerProperty(default=-1)

    @webapp2.cached_property
    def kind(self):
        return self.key.kind()

    def index_doc(self):
        doc = search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(name='slug', value=tokenize(self.key.string_id())),
                search.TextField(name='author', value=' '.join(self.author.nickname().split('.'))),
                search.TextField(name='tags', value=' '.join(self.tags)),
                search.NumberField(name='year', value=self.year),
                search.NumberField(name='month', value=self.date.month),
                search.HtmlField(name='body', value=self.body)]
        )
        INDEX.put(doc)

    def add(self, data):
        self.headline = data['headline']
        self.summary = data['summary']
        self.date = data['date']
        self.body = data['body']
        self.tags = data['tags']
        self.put()

        for indx, obj in enumerate(data['newimages']):
            if obj['name'] and isinstance(obj['blob'], cgi.FieldStorage):
                img = Img(
                    parent=self.key,
                    id='%s_%s' % (self.key.string_id(), indx),
                    num=indx,
                    name=obj['name'],
                    blob=obj['blob'].value
                )
                img.mime = obj['blob'].headers['Content-Type']
                img.put()

        incr_count(self.kind, 'author', self.author.nickname())
        incr_count(self.kind, 'date', self.year)
        update_tags(self.kind, None, self.tags)
        deferred.defer(self.index_doc)

    def edit(self, data):
        self.headline = data['headline']
        self.summary = data['summary']
        self.date = data['date']
        self.body = data['body']
        self.front = data['front']

        for indx, obj in enumerate(data['images']):
            id = '%s_%s' % (self.key.string_id(), indx)
            if obj['delete']:
                key = ndb.Key('Entry', self.key.string_id(), 'Img', id)
                key.delete()
                if indx == self.front:
                    self.front = -1

        for indx, obj in enumerate(data['newimages'], start=self.image_list.count()):
            id = '%s_%s' % (self.key.string_id(), indx)
            if obj['name'] and isinstance(obj['blob'], cgi.FieldStorage):
                img = Img(
                    parent=self.key,
                    id=id,
                    num=indx,
                    name=obj['name'],
                    blob=obj['blob'].value
                )
                img.mime = obj['blob'].headers['Content-Type']
                img.put()

        old = self.date
        new = data['date']
        if old != new:
            decr_count(self.kind, 'date', self.year)
            incr_count(self.kind, 'date', new.year)
        update_tags(self.kind, self.tags, data['tags'])
        self.tags = sorted(data['tags'])

        self.put()

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        deferred.defer(remove_doc, key.urlsafe())

        decr_count(key.kind(), 'author', obj.author.nickname())
        decr_count(key.kind(), 'date', obj.year)
        update_tags(key.kind(), obj.tags, None)

        ndb.delete_multi([x.key for x in ndb.Query(ancestor=key) if x.key != key])

    @property
    def image_list(self):
        return Img.query(ancestor=self.key).order(Img.num)

    def image_url(self, num):
        return '/entries/image/%s_%s' % (self.key.string_id(), num)

    @classmethod
    def query_for(cls, field, value):
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)

    def serialize(self):
        data = self.to_dict(exclude=('front', 'year'))
        data.update({
            'slug': self.key.string_id(),
            'url': webapp2.uri_for('entry', slug=self.key.string_id()),
        })
        return data
