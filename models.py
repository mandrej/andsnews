from __future__ import division

__author__ = 'milan'

import datetime
import cgi
import math
import colorsys
import bisect
import itertools
import logging
import collections
import webapp2
from cStringIO import StringIO
from decimal import *

from string import capitalize
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.api import users, memcache, search, images

from lib import colorific
from lib.exifread import process_file
from config import COLORS, ASA, LENGTHS, HUE, LUM, SAT, TIMEOUT

INDEX = search.Index(name='searchindex')
KEYS = ['Photo_tags', 'Photo_author', 'Photo_date',
        'Photo_model', 'Photo_lens', 'Photo_eqv', 'Photo_iso', 'Photo_color',
        'Entry_tags', 'Entry_author', 'Entry_date',
        'Feed_tags',
        'Comment_forkind', 'Comment_author', 'Comment_date']
PHOTO_FIELDS = ('model', 'lens', 'eqv', 'iso', 'color',)
ENTRY_IMAGES = 10
LOGARITHMIC, LINEAR = 1, 2


def rounding(val, values):
    i = bisect.bisect_right(values, val)
    try:
        prev, next = values[i-1: i+1]
    except ValueError:
        logging.error('Could not round {0}'.format(val))
    else:
        if abs(prev-val) <= abs(next-val):
            return prev
        else:
            return next


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
    elif field == 'forkind':
        value = capitalize(value)
    try:
        value = int(value)
    except (ValueError, TypeError):
        pass
    return {field: value}


def img_palette(buff):
    img = images.Image(buff)
    img.resize(width=100, height=100)
    thumb = img.execute_transforms(output_encoding=images.JPEG, quality=86)
    return colorific.extract_colors(StringIO(thumb))


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
    #     deg_min_sec = eval(tags['GPS GPSLatitude'].printable)  # [44, 47, 559597/10000]
    #     data['latitude'] = sum(map(divide60, enumerate(deg_min_sec)))  # [(0, 44), (1, 47), (2, 55.9597)]

    # if 'GPS GPSLongitude' in tags:
    #     d, m, s = eval(tags['GPS GPSLongitude'].printable)  # [20, 28, 508547/10000]
    #     data['longitude'] = d + m / 60 + s / 3600

    return data


def range_names(rgb):
    def in_range(value, component):
        for x in component:
            if value in x['span']:
                return x['name']

    rel_rgb = map(lambda x: x / 255, rgb)
    h, l, s = colorsys.rgb_to_hls(*rel_rgb)
    hue = in_range(int(round(h * 360)), HUE)
    lum = in_range(int(round(l * 100)), LUM)
    sat = in_range(int(round(s * 100)), SAT)
    return hue, lum, sat


def update_doc(doc_id, headline, author, body='', tags=[], date=None):
    doc = search.Document(
        doc_id=doc_id,
        fields=[
            search.TextField(name='headline', value=headline),
            search.TextField(name='author', value=author.nickname()),
            search.HtmlField(name='body', value=body),
            search.TextField(name='tags', value=','.join(tags)),
            search.DateField(name='date', value=date.date())]
    )
    INDEX.put(doc)


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


class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.GenericProperty(required=True)  # could be int as str
    count = ndb.IntegerProperty(default=0)


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
    deferred.defer(update_counter, 1, *args)


def decr_count(*args):
    deferred.defer(update_counter, -1, *args)


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

    def characterise(self):
        if self.lum in ('dark', 'light',) or self.sat == 'monochrome':
            return self.lum
        else:
            return self.hue

    color = ndb.ComputedProperty(characterise)

    @webapp2.cached_property
    def kind(self):
        return self.key.kind()

    @webapp2.cached_property
    def index_data(self):
        return {
            'doc_id': self.key.urlsafe(),
            'headline': self.headline,
            'author': self.author,
            'body': '%s %s' % (self.model, self.lens),
            'tags': self.tags,
            'date': self.date
        }

    def add(self, data):
        blob_info = blobstore.parse_blob_info(data['photo'])

        self.headline = data['headline']
        self.blob_key = blob_info.key()
        self.size = blob_info.size
        self.tags = data['tags']

        blob_reader = blobstore.BlobReader(blob_info, buffer_size=1024*1024)  # Max 1MB
        buff = blob_reader.read()
        exif = get_exif(buff)
        for field, value in exif.items():
            setattr(self, field, value)

        palette = img_palette(buff)
        if palette.bgcolor:
            self.rgb = palette.bgcolor.value
        else:
            self.rgb = palette.colors[0].value
        self.hue, self.lum, self.sat = range_names(self.rgb)
        self.put()

        incr_count(self.kind, 'author', self.author.nickname())
        incr_count(self.kind, 'date', self.year)
        update_tags(self.kind, None, self.tags)
        for field in PHOTO_FIELDS:
            value = data.get(field, None)
            if value:
                incr_count(self.kind, field, value)
        deferred.defer(update_doc, **self.index_data)

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
        deferred.defer(update_doc, **self.index_data)

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        deferred.defer(remove_doc, key.urlsafe())

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
    def normal_url_async(self):
        return images.get_serving_url_async(self.blob_key, size=0, crop=False, secure_url=True)

    @webapp2.cached_property
    def small_url_async(self):
        return images.get_serving_url_async(self.blob_key, size=300, crop=True, secure_url=True)

    @webapp2.cached_property
    def blob_info(self):
        return blobstore.BlobInfo.get(self.blob_key)

    @webapp2.cached_property
    def hex(self):
        return '#%02x%02x%02x' % tuple(self.rgb)

    @webapp2.cached_property
    def hls(self):
        rel_rgb = map(lambda x: x / 255, self.rgb)
        h, l, s = colorsys.rgb_to_hls(*rel_rgb)
        return int(round(h * 360)), int(round(l * 100)), int(round(s * 100))

    @webapp2.cached_property
    def similar(self):
        return COLORS[self.color]

    def comment_list(self):
        return Comment.query(ancestor=self.key).order(-Comment.date)

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

    @webapp2.cached_property
    def index_data(self):
        return {
            'doc_id': self.key.urlsafe(),
            'headline': self.headline,
            'author': self.author,
            'body': '%s %s' % (self.summary, self.body),
            'tags': self.tags,
            'date': self.date
        }

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
        deferred.defer(update_doc, **self.index_data)

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
        deferred.defer(update_doc, **self.index_data)

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        deferred.defer(remove_doc, key.urlsafe())

        decr_count(key.kind(), 'author', obj.author.nickname())
        decr_count(key.kind(), 'date', obj.year)
        update_tags(key.kind(), obj.tags, None)

        ndb.delete_multi([x.key for x in ndb.Query(ancestor=key) if x.key != key])

    def comment_list(self):
        return Comment.query(ancestor=self.key).order(-Comment.date)

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


class Comment(ndb.Model):
    # parent Photo, Entry
    author = ndb.UserProperty(auto_current_user_add=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    year = ndb.IntegerProperty()
    forkind = ndb.StringProperty(default='Application')
    body = ndb.TextProperty(required=True)

    @webapp2.cached_property
    def kind(self):
        return self.key.kind()

    @webapp2.cached_property
    def index_data(self):
        return {
            'doc_id': self.key.urlsafe(),
            'headline': '' if self.is_message else self.key.parent().get().headline,
            'author': self.author,
            'body': '%s' % self.body,
            'date': self.date
        }

    @webapp2.cached_property
    def is_message(self):
        return self.forkind == 'Application'

    def add(self):
        self.put()

        incr_count(self.kind, 'author', self.author.nickname())
        if self.is_message:
            incr_count(self.kind, 'forkind', 'Application')
        else:
            incr_count(self.key.parent().kind(), 'comment', self.key.parent().id())
            incr_count('Comment', 'forkind', self.key.parent().kind())
        incr_count('Comment', 'date', self.year)
        deferred.defer(update_doc, **self.index_data)

    def _pre_put_hook(self):
        self.year = self.date.year

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        deferred.defer(remove_doc, key.urlsafe())

        decr_count(key.kind(), 'author', obj.author.nickname())
        decr_count(key.kind(), 'date', obj.year)
        if obj.is_message:
            decr_count(key.kind(), 'forkind', 'Application')
        else:
            decr_count(key.parent().kind(), 'comment', key.parent().id())
            decr_count(key.kind(), 'forkind', key.parent().kind())

    @classmethod
    def query_for(cls, field, value):
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)


class Feed(ndb.Model):
    url = ndb.StringProperty(required=True)
    headline = ndb.StringProperty(required=True)
    subtitle = ndb.StringProperty()
    author = ndb.UserProperty(auto_current_user_add=True)
    tags = ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty()

    @webapp2.cached_property
    def kind(self):
        return self.key.kind()

    def add(self, data):
        self.url = data['url']
        self.headline = data['headline']
        self.tags = data['tags']
        self.put()
        for name in self.tags:
            incr_count('Feed', 'tags', name)

    def edit(self, data):
        update_tags(self.kind, self.tags, data['tags'])
        self.tags = sorted(data['tags'])
        self.url = data['url']
        self.headline = data['headline']
        self.put()

    @classmethod
    def _pre_delete_hook(cls, key):
        obj = key.get()
        update_tags(key.kind(), obj.tags, None)
        memcache.delete(key.string_id())

    @classmethod
    def query_for(cls, field, value):
        f = filter_param(field, value)
        filters = [cls._properties[k] == v for k, v in f.items()]
        return cls.query(*filters).order(-cls.date)