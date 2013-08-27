from __future__ import division
import logging
import datetime
import time
import cgi
import colorsys
import itertools
import collections
from cStringIO import StringIO
from decimal import *

from PIL import Image
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.api import users, memcache, search, images

from lib import colorific
from exifread import process_file
from cloud import calculate_cloud
from config import COLORS, HUE, LUM, SAT, TIMEOUT


INDEX = search.Index(name='searchindex')

KEYS = ['Photo_tags', 'Photo_author', 'Photo_date',
        'Photo_model', 'Photo_lens', 'Photo_eqv', 'Photo_iso', 'Photo_color',
        'Entry_tags', 'Entry_author', 'Entry_date',
        'Feed_tags',
        'Comment_forkind', 'Comment_author', 'Comment_date']
PHOTO_FIELDS = ('model', 'lens', 'eqv', 'iso', 'color',)
ENTRY_IMAGES = 10


def img_palette(buff):
    img = Image.open(StringIO(buff))
    return colorific.extract_colors(img.resize((100, 100)))


def get_exif(buff):
    data = {}
    tags = process_file(StringIO(buff), details=False)
    if 'Image Make' in tags and 'Image Model' in tags:
        make = tags['Image Make'].printable.replace('/', '')
        model = tags['Image Model'].printable.replace('/', '')
        s1 = set(make.split())
        s2 = set(model.split())
        if not s1 & s2:
            data['model'] = ' '.join(list(s1 - s2) + list(s2 - s1))
        else:
            data['model'] = model
    elif 'Image Model' in tags:
        data['model'] = tags['Image Model'].printable.replace('/', '')

    if 'EXIF LensModel' in tags:
        data['lens'] = tags['EXIF LensModel'].printable.replace('/', '')

    if 'EXIF DateTimeOriginal' in tags:
        dt_tuple = time.strptime(tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
        epochsec = time.mktime(dt_tuple)
        data['date'] = datetime.datetime.fromtimestamp(epochsec)
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
        getcontext().prec = 1
        data['iso'] = int(Decimal(tags['EXIF ISOSpeedRatings'].printable) / 1)

    logging.info(data)
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


def create_doc(id, headline='', author=None, body='', tags=[], date=None):
    return search.Document(doc_id=id, fields=[
        search.TextField(name='headline', value=headline),
        search.TextField(name='author', value=author.nickname()),
        search.HtmlField(name='body', value=body),
        search.TextField(name='tags', value=','.join(tags)),
        search.DateField(name='date', value=date.date()),
    ])


def remove_doc(safe_key):
    return INDEX.delete(safe_key)


class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.GenericProperty(required=True)  # could be int as str
    count = ndb.IntegerProperty(default=0)


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


def update_counter(*args, **kwargs):
    delta = kwargs.get('delta', 1)
    key_name = '%s||%s||%s' % args
    params = dict(zip(('forkind', 'field', 'value'), args))

    obj = Counter.get_or_insert(key_name, **params)
    obj.count += delta
    obj.put()

    mem_key = '{forkind}_{field}'.format(**params)
    cloud = Cloud(mem_key)
    cloud.update(params['value'], delta)


def incr_count(*args):
    deferred.defer(update_counter, *args, delta=1)


def decr_count(*args):
    deferred.defer(update_counter, *args, delta=-1)


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
    color = ndb.ComputedProperty(lambda self: self.hue if self.sat == 'color' else self.lum)

    def index_add(self):
        return INDEX.put(
            create_doc(
                self.key.urlsafe(),
                headline=self.headline,
                author=self.author,
                body='%s %s' % (self.model, self.lens),
                tags=self.tags,
                date=self.date))

    def _put(self):
        self.put()
        self.index_add()

    def add(self, data):
        blob_info = blobstore.parse_blob_info(data['photo'])
        self.headline = data['headline']
        self.blob_key = blob_info.key()
        self.size = blob_info.size
        blob_reader = blob_info.open()
        buff = blob_reader.read()
        palette = img_palette(buff)
        self.rgb = palette.colors[0].value
        exif = get_exif(buff)
        for field, value in exif.items():
            setattr(self, field, value)
        self.hue, self.lum, self.sat = range_names(self.rgb)
        self.tags = data['tags']
        self._put()

        for name in self.tags:
            incr_count('Photo', 'tags', name)
        incr_count('Photo', 'author', self.author.nickname())
        incr_count('Photo', 'date', self.year)
        for field in PHOTO_FIELDS:
            value = data.get(field, None)
            if value:
                incr_count('Photo', field, value)

    def edit(self, data):
        old = self.author
        new = data['author']
        if new != old.nickname():
            # TODO Not all emails are gmail
            self.author = users.User(email='%s@gmail.com' % new)
            decr_count('Photo', 'author', old.nickname())
            incr_count('Photo', 'author', self.author.nickname())
        del data['author']

        old_tags = set(self.tags)
        new_tags = set(data['tags'])
        if old_tags - new_tags:
            for name in list(old_tags - new_tags):
                decr_count('Photo', 'tags', name)
        if new_tags - old_tags:
            for name in list(new_tags - old_tags):
                incr_count('Photo', 'tags', name)
        self.tags = sorted(new_tags)
        del data['tags']

        old = self.date
        new = data['date']
        if old != new:
            decr_count('Photo', 'date', self.year)
            incr_count('Photo', 'date', new.year)
        else:
            del data['date']

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
            data['eqv'] = int(10 * round(self.focal_length * self.crop_factor / 10))

        for field, value in data.items():
            if field in PHOTO_FIELDS:
                old = getattr(self, field)
                new = data.get(field)
                if old != new:
                    if old:
                        decr_count('Photo', field, old)
                    if new:
                        incr_count('Photo', field, new)
                    setattr(self, field, new)
            else:
                setattr(self, field, value)

        self._put()

    @classmethod
    def _pre_delete_hook(cls, key):
        instance = key.get()
        deferred.defer(remove_doc, key.urlsafe())

        blob_info = blobstore.BlobInfo.get(instance.blob_key)
        blob_info.delete()

        for name in instance.tags:
            decr_count('Photo', 'tags', name)
        decr_count('Photo', 'author', instance.author.nickname())
        decr_count('Photo', 'date', instance.year)
        for field in PHOTO_FIELDS:
            value = getattr(instance, field)
            if value:
                decr_count('Photo', field, value)

        ndb.delete_multi([x.key for x in ndb.Query(ancestor=key) if x.key != key])

    def cached_url(self, size, crop):
        pattern = '%s=s%s-c' if crop else '%s=s%s'
        key = pattern % (self.key.string_id(), size)
        url = memcache.get(key)
        if url is None:
            url = images.get_serving_url(self.blob_key, size=size, crop=crop)
            memcache.add(key, url)
        return url

    def normal_url(self):
        return self.cached_url(1000, False)

    def small_url(self):
        return self.cached_url(375, False)

    @property
    def blob_info(self):
        return blobstore.BlobInfo.get(self.blob_key)

    @property
    def hex(self):
        return '#%02x%02x%02x' % tuple(self.rgb)

    @property
    def hls(self):
        rel_rgb = map(lambda x: x / 255, self.rgb)
        h, l, s = colorsys.rgb_to_hls(*rel_rgb)
        return int(round(h * 360)), int(round(l * 100)), int(round(s * 100))

    def comment_list(self):
        return Comment.query(ancestor=self.key).order(-Comment.date)


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

    def index_add(self):
        return INDEX.put(
            create_doc(
                self.key.urlsafe(),
                headline=self.headline,
                author=self.author,
                body='%s %s' % (self.summary, self.body),
                tags=self.tags,
                date=self.date))

    def _put(self):
        self.put()
        self.index_add()

    def add(self, data):
        self.headline = data['headline']
        self.summary = data['summary']
        self.date = data['date']
        self.body = data['body']
        self.tags = data['tags']
        self._put()

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

        incr_count('Entry', 'author', self.author.nickname())
        incr_count('Entry', 'date', self.year)
        for name in self.tags:
            incr_count('Entry', 'tags', name)

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
            decr_count('Entry', 'date', self.year)
            incr_count('Entry', 'date', new.year)

        old_tags = set(self.tags)
        new_tags = set(data['tags'])
        if old_tags - new_tags:
            for name in list(old_tags - new_tags):
                decr_count('Entry', 'tags', name)
        if new_tags - old_tags:
            for name in list(new_tags - old_tags):
                incr_count('Entry', 'tags', name)
        self.tags = sorted(new_tags)

        self._put()

    @classmethod
    def _pre_delete_hook(cls, key):
        instance = key.get()
        deferred.defer(remove_doc, key.urlsafe())

        decr_count('Entry', 'author', instance.author.nickname())
        decr_count('Entry', 'date', instance.year)
        for name in instance.tags:
            decr_count('Entry', 'tags', name)

        ndb.delete_multi([x.key for x in ndb.Query(ancestor=key) if x.key != key])

    def comment_list(self):
        return Comment.query(ancestor=self.key).order(-Comment.date)

    @property
    def image_list(self):
        return Img.query(ancestor=self.key).order(Img.num)

    def image_url(self, num):
        return '/entries/image/%s_%s' % (self.key.string_id(), num)


class Comment(ndb.Model):
    # parent Photo, Entry
    author = ndb.UserProperty(auto_current_user_add=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    year = ndb.IntegerProperty()
    forkind = ndb.StringProperty(default='Application')
    body = ndb.TextProperty(required=True)

    def index_add(self):
        return INDEX.put(
            create_doc(
                self.key.urlsafe(),
                headline='' if self.is_message else self.key.parent().get().headline,
                author=self.author,
                body=self.body,
                date=self.date))

    @property
    def is_message(self):
        return self.forkind == 'Application'

    def add(self):
        self.put()
        self.index_add()

        incr_count('Comment', 'author', self.author.nickname())
        if self.is_message:
            incr_count('Comment', 'forkind', 'Application')
        else:
            incr_count(self.key.parent().kind(), 'comment', self.key.parent().id())
            incr_count('Comment', 'forkind', self.key.parent().kind())
        incr_count('Comment', 'date', self.year)

    def _pre_put_hook(self):
        self.year = self.date.year

    @classmethod
    def _pre_delete_hook(cls, key):
        instance = key.get()
        deferred.defer(remove_doc, key.urlsafe())

        decr_count('Comment', 'author', instance.author.nickname())
        if instance.is_message:
            decr_count('Comment', 'forkind', 'Application')
        else:
            decr_count(key.parent().kind(), 'comment', key.parent().id())
            decr_count('Comment', 'forkind', key.parent().kind())
        decr_count('Comment', 'date', instance.year)


class Feed(ndb.Model):
    url = ndb.StringProperty(required=True)
    headline = ndb.StringProperty(required=True)
    subtitle = ndb.StringProperty()
    author = ndb.UserProperty(auto_current_user_add=True)
    tags = ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty()

    def add(self, data):
        self.url = data['url']
        self.headline = data['headline']
        self.tags = data['tags']
        self.put()
        for name in self.tags:
            incr_count('Feed', 'tags', name)

    def edit(self, data):
        old_tags = set(self.tags)
        new_tags = set(data['tags'])
        if old_tags - new_tags:
            for name in list(old_tags - new_tags):
                decr_count('Feed', 'tags', name)
        if new_tags - old_tags:
            for name in list(new_tags - old_tags):
                incr_count('Feed', 'tags', name)
        self.tags = sorted(new_tags)

        self.url = data['url']
        self.headline = data['headline']
        self.put()

    @classmethod
    def _pre_delete_hook(cls, key):
        instance = key.get()
        for name in instance.tags:
            decr_count('Feed', 'tags', name)
        memcache.delete(key.string_id())