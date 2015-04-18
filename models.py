from __future__ import division

__author__ = 'milan'

import datetime
import cgi
import math
import colorsys
import itertools
import collections
import webapp2
from cStringIO import StringIO
from decimal import *
from PIL import Image
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.api import users, memcache, images

from palette import extract_colors, rgb_to_hex
from exifread import process_file
from config import COLORS, ASA, LENGTHS, HUE, LUM, SAT, TIMEOUT

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
    EXIF tags:
    ColorSpace, ComponentsConfiguration, DateTimeDigitized, DateTimeOriginal, ExifImageLength, ExifImageWidth,
    ExifVersion, ExposureTime, FNumber, FlashPixVersion, FocalLength, ISOSpeedRatings, InteroperabilityOffset
    
    GPS tags:
    GPSAltitude, GPSAltitudeRef, GPSDate, GPSImgDirection, GPSImgDirectionRef, GPSLatitude, GPSLatitudeRef,
    GPSLongitude, GPSLongitudeRef, GPSProcessingMethod, GPSTimeStamp, GPSVersionID
    
    Image tags:
    ExifOffset, GPSInfo, Make, Model, ResolutionUnit, Software, XResolution, YCbCrPositioning, YResolution
    
    Thumbnail tags:
    Compression, JPEGInterchangeFormat, JPEGInterchangeFormatLength, ResolutionUnit, XResolution, YResolution
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
        data['aperture'] = float(Decimal(eval(tags['EXIF FNumber'].printable)) / 1)

    if 'EXIF ExposureTime' in tags:
        data['shutter'] = tags['EXIF ExposureTime'].printable

    if 'EXIF FocalLength' in tags:
        getcontext().prec = 2
        data['focal_length'] = float(Decimal(eval(tags['EXIF FocalLength'].printable)) / 1)

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
    rel_rgb = map(lambda x: x/255, rgb)
    h, l, s = colorsys.rgb_to_hls(*rel_rgb)
    return int(round(h * 360)), int(round(l * 100)), int(round(s * 100))


def range_names(rgb):
    def in_range(value, component):
        for x in component:
            if value in x['span']:
                return x['name']

    h, l, s = rgb_hls(rgb)
    hue = in_range(h % 360, HUE)
    lum = in_range(l, LUM)
    sat = in_range(s, SAT)
    return hue, lum, sat


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
        content = []
        if self.field == 'color':
            for k, count in collection.items():
                data = COLORS[k]
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


def update_counter(delta, *args):
    key_name = '%s||%s||%s' % args
    params = dict(zip(('forkind', 'field', 'value'), args))

    obj = Counter.get_or_insert(key_name, **params)
    obj.count += delta
    obj.put()

    mem_key = '{forkind}_{field}'.format(**params)
    cloud = Cloud(mem_key)
    cloud.update(params['value'], delta)


def incr_count(*args):
    deferred.defer(update_counter, 1, *args, _queue='queue25')


def decr_count(*args):
    deferred.defer(update_counter, -1, *args, _queue='queue25')


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
    crop_factor = ndb.FloatProperty(default=1.6)
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

    ratio = ndb.ComputedProperty(
        lambda self: self.dim[0] / self.dim[1] if self.dim and len(self.dim) == 2 else 1.5)

    color = ndb.ComputedProperty(
        lambda self: self.lum if self.lum in ('dark', 'light',) or self.sat == 'monochrome' else self.hue)

    @webapp2.cached_property
    def kind(self):
        return self.key.kind()

    @webapp2.cached_property
    def buffer(self):
        blob_reader = blobstore.BlobReader(self.blob_key, buffer_size=1024*1024)
        return blob_reader.read(size=-1)

    @webapp2.cached_property
    def image_from_buffer(self):
        return Image.open(StringIO(self.buffer))

    def exif_values(self):
        exif = get_exif(self.buffer)
        for field, value in exif.items():
            setattr(self, field, value)

    def dim_values(self):
        self.dim = self.image_from_buffer.size  # (width, height) tuple

    def palette_values(self):
        img = self.image_from_buffer
        img.thumbnail((100, 100), Image.ANTIALIAS)
        palette = extract_colors(img)
        if palette.bgcolor:
            colors = [palette.bgcolor] + palette.colors
        else:
            colors = palette.colors

        max = 0
        for c in colors:
            h, l, s = rgb_hls(c.value)
            criteria = s * c.prominence
            if criteria > max:
                max = criteria
                self.rgb = c.value

        self.hue, self.lum, self.sat = range_names(self.rgb)

    def add(self, data, blob_info):
        try:
            self.headline = data['headline']
            # TODO Not all emails are gmail
            self.author = users.User(email='%s@gmail.com' % data['author'])
            self.blob_key = blob_info.key()
            self.size = blob_info.size
            self.tags = data['tags']

            self.exif_values()
            self.dim_values()
            self.palette_values()
        except (blobstore.Error, Exception):
            blob_info.delete()
        else:
            self.put()

            incr_count(self.kind, 'author', self.author.nickname())
            incr_count(self.kind, 'date', self.year)
            update_tags(self.kind, None, self.tags)
            for field in PHOTO_FIELDS:
                value = getattr(self, field, None)
                if value:
                    incr_count(self.kind, field, value)

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

        blob_info = blobstore.BlobInfo.get(obj.blob_key)
        blob_info.delete()

        decr_count(key.kind(), 'author', obj.author.nickname())
        decr_count(key.kind(), 'date', obj.year)
        update_tags(key.kind(), obj.tags, None)
        for field in PHOTO_FIELDS:
            value = getattr(obj, field)
            if value:
                decr_count(key.kind(), field, value)
        ndb.delete_multi([x.key for x in ndb.Query(ancestor=key) if x.key != key])

    @webapp2.cached_property
    def serving_url(self):
        return images.get_serving_url(self.blob_key, crop=False, secure_url=True)

    @webapp2.cached_property
    def blob_info(self):
        return blobstore.BlobInfo.get(self.blob_key)

    @webapp2.cached_property
    def hex(self):
        return rgb_to_hex(tuple(self.rgb))

    @webapp2.cached_property
    def hls(self):
        return rgb_hls(self.rgb)

    @webapp2.cached_property
    def similar(self):
        return COLORS[self.color]

    @classmethod
    def query_for(cls, field, value):
        """[FilterNode('color', '=', 'pink')]"""
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)


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
