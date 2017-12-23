from __future__ import division

import colorsys
import datetime
import logging
import time
import uuid
from cStringIO import StringIO
from decimal import *

import cloudstorage as gcs
import re
import webapp2
from PIL import Image
from exifread import process_file
from google.appengine.api import users, search, images
from google.appengine.ext import ndb, deferred, blobstore

from config import ASA, HUE, LUM, SAT, BUCKET
from palette import extract_colors, rgb_to_hex
from slugify import slugify

logger = logging.getLogger('modules')
logger.setLevel(level=logging.DEBUG)

INDEX = search.Index(name='searchindex')
PHOTO_FILTER = ['year', 'tags', 'model', 'color']


def rounding(val, values):
    return min(values, key=lambda x: abs(x - val))


# def sizeof_fmt(num, suffix='B'):
#     for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
#         if abs(num) < 1024.0:
#             return "%3.1f%s%s" % (num, unit, suffix)
#         num /= 1024.0
#     return "%.1f%s%s" % (num, 'Y', suffix)


def filter_param(field, value):
    try:
        assert field and value
    except AssertionError:
        return {}

    if field == 'author':
        value = users.User(email=value)
    elif field == 'iso':
        value = int(value)

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


class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.GenericProperty(required=True)
    count = ndb.IntegerProperty(default=0)


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
                search.NumberField(name='month', value=self.date.month),
                search.TextField(name='model', value=self.model),
                search.NumberField(name='stamp', value=time.mktime(self.date.timetuple())),
                search.TextField(name='color', value=self.color),
            ]
        )
        INDEX.put(doc)

    def update_filters(self, new_pairs, old_pairs):
        counters = []
        for i, (field, value) in enumerate(set(new_pairs) | set(old_pairs)):
            key_name = 'Photo||{}||{}'.format(field, value)
            counter = Counter.get_or_insert(key_name, forkind='Photo', field=field, value=value)

            if (field, value) in old_pairs:
                counter.count -= 1
            if (field, value) in new_pairs:
                counter.count += 1
            counters.append(counter)

        ndb.put_multi(counters)

    def changed_pairs(self):
        """
        List of changed field, value pairs
        [('year', 2017), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro'), ('color', 'blue')]
        """
        pairs = []
        for field in PHOTO_FILTER:
            value = getattr(self, field, None)
            if value:
                if isinstance(value, (list, tuple)):
                    for v in value:
                        pairs.append((field, str(v)))
                elif isinstance(value, users.User):
                    pairs.append((field, value.email()))
                elif isinstance(value, int):
                    pairs.append((field, value))
                else:
                    pairs.append((field, str(value)))  # stringify year
        return pairs

    @webapp2.cached_property
    def buffer(self):
        blob_reader = blobstore.BlobReader(self.blob_key, buffer_size=1024*1024)
        return blob_reader.read(size=-1)

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
            self.author = users.User(email='milan.andrejevic@gmail.com')  # FORCE FIELD
            self.tags = ['new']  # ARTIFICIAL TAG
            self.put()

            new_pairs = self.changed_pairs()
            deferred.defer(self.update_filters, new_pairs, [], _queue='background')
            return {'success': True, 'safe_key':  self.key.urlsafe()}

    def edit(self, data):
        old_pairs = self.changed_pairs()

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

        new_pairs = self.changed_pairs()
        deferred.defer(self.index_doc, _queue='background')
        deferred.defer(self.update_filters, new_pairs, old_pairs, _queue='background')

    def remove(self):
        old_pairs = self.changed_pairs()

        # blobstore.delete(self.blob_key)
        images.delete_serving_url(self.blob_key)
        self.key.delete()
        time.sleep(3)

        deferred.defer(remove_doc, self.key.urlsafe(), _queue='background')
        deferred.defer(self.update_filters, [], old_pairs, _queue='background')

    @webapp2.cached_property
    def serving_url(self):
        try:
            return images.get_serving_url(self.blob_key, crop=False, secure_url=True)
        except (images.ObjectNotFoundError, images.TransformationError) as e:
            # raise _ToImagesError(e, readable_blob_key)
            logger.error(e.message)
            return None

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

    def serialize(self):
        data = self.to_dict(exclude=(
            'blob_key', 'size', 'ratio', 'crop_factor', 'dim',
            'rgb', 'sat', 'lum', 'hue', 'year', 'filename'))
        data.update({
            'kind': 'photo',
            'year': str(self.year),
            'safekey': self.key.urlsafe(),
            'serving_url': self.serving_url,
            # 'size': sizeof_fmt(self.size),
        })
        return data
