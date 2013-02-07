from __future__ import division
import webapp2, logging
import datetime, time, colorsys
from cStringIO import StringIO
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.api import users, memcache, search, images
from lib.EXIF import process_file
from settings import DEVEL, HUE, LUM, SAT

INDEX = search.Index(name='searchindex')

KEYS = ['Photo_tags', 'Photo_author', 'Photo_date',
        'Photo_model', 'Photo_lens', 'Photo_eqv', 'Photo_iso', 'Photo_colors',
        'Entry_tags', 'Entry_author', 'Entry_date',
        'Feed_tags',
        'Comment_forkind', 'Comment_author', 'Comment_date']
PHOTO_FIELDS = ('model', 'lens', 'eqv', 'iso',)
ENTRY_IMAGES = 10

def median(buff):
    triple = []
    histogram = images.histogram(buff)
    for band in histogram:
        suma = 0
        limit = sum(band)/2
        for i in xrange(256):
            suma += band[i]
            if (suma > limit):
                triple.append(i)
                break
    return triple

def get_exif(buff):
    data = {}
    if DEVEL:
        tags = process_file(StringIO(buff), details=False)
        if 'Image Make' in tags and 'Image Model' in tags:
            make = tags['Image Make'].printable.replace('/', '')
            model = tags['Image Model'].printable.replace('/', '')
            s1 = set(make.split())
            s2 = set(model.split())
            if not s1&s2:
                data['model'] = ' '.join(list(s1-s2) + list(s2-s1))
            else:
                data['model'] = model
        elif 'Image Model' in tags:
            data['model'] = tags['Image Model'].printable.replace('/', '')

        if 'EXIF DateTimeOriginal' in tags:
            dt_tuple = time.strptime(tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
            epochsec = time.mktime(dt_tuple)
            data['date'] = datetime.datetime.fromtimestamp(epochsec)
        else:
            data['date'] = datetime.datetime.now()

        if 'EXIF FNumber' in tags:
            data['aperture'] = round(float(eval('%s.0' % tags['EXIF FNumber'].printable)), 1)

        if 'EXIF ExposureTime' in tags:
            data['shutter'] = tags['EXIF ExposureTime'].printable

        if 'EXIF FocalLength' in tags:
            value = float(eval('%s.0' % tags['EXIF FocalLength'].printable))
            data['focal_length'] = round(value, 1)

        if 'EXIF ISOSpeedRatings' in tags:
            data['iso'] = int(tags['EXIF ISOSpeedRatings'].printable)
    else:
        img = images.Image(buff)
        img.rotate(0)
        img.execute_transforms(output_encoding=images.JPEG, parse_source_metadata=True)
        tags = img.get_original_metadata()
        if 'Make' in tags and 'Model' in tags:
            make = tags['Make']
            make = make.replace('/', '')
            model = tags['Model']
            model = model.replace('/', '')
            s1 = set(make.split())
            s2 = set(model.split())
            if not s1&s2:
                data['model'] = ' '.join(list(s1-s2) + list(s2-s1))
            else:
                data['model'] = model
        elif 'Model' in tags:
            model = tags['Model']
            model = model.replace('/', '')
            data['model'] = model

        elif 'Lens' in tags:
            lens = tags['Lens']
            data['lens'] = lens.replace('/', '')

        if 'DateTimeDigitized' in tags:
            date = tags['DateTimeDigitized']
            dt_tuple = time.strptime(date, '%Y:%m:%d %H:%M:%S')
            epochsec = time.mktime(dt_tuple)
            data['date'] = datetime.datetime.fromtimestamp(epochsec)
        else:
            data['date'] = datetime.datetime.now()

        if 'FNumber' in tags:
            data['aperture'] = round(float(tags['FNumber']), 1)

        if 'ExposureTime' in tags:
            shutter = tags['ExposureTime']
            if shutter < 1:
                shutter = '1/%s' % round(1/shutter)
                data['shutter'] = shutter

        if 'FocalLength' in tags:
            data['focal_length'] = round(float(tags['FocalLength']), 1)

        if 'ISOSpeedRatings' in tags:
            iso = tags['ISOSpeedRatings']
            data['iso'] = int(iso)

    logging.info(data)
    return data

def range_names(rgb):
    def in_range(value, component):
        for x in component:
            if value in x['span']:
                return x['name']

    rel_rgb = map(lambda x: x/255, rgb)
    h, l, s = colorsys.rgb_to_hls(*rel_rgb)
    H, L, S = int(h*360), int(l*100), int(s*100)
    hue = in_range(H, HUE)
    lum = in_range(L, LUM)
    sat = in_range(S, SAT)
    return hue, lum, sat

def create_doc(id, headline='', author=None, body='', tags=[], date=None, url=None, kind=None):
    return search.Document(
        doc_id=id, fields=[
            search.TextField(name='headline', value=headline),
            search.TextField(name='author', value=author.nickname()),
            search.HtmlField(name='body', value=body),
            search.TextField(name='tags', value=', '.join(tags)),
            search.DateField(name='date', value=date.date()),
            search.AtomField(name='link', value=url),
            search.AtomField(name='kind', value=kind)
    ], language='en_US')

class Counter(ndb.Model):
    forkind = ndb.StringProperty(required=True)
    field = ndb.StringProperty(required=True)
    value = ndb.StringProperty(required=True)
    count = ndb.IntegerProperty(default=0)

def update_counter(*args, **kwargs):
    key = '%s||%s||%s' % args
    params = dict(zip(('forkind', 'field', 'value'), map(str, args)))
    obj = Counter.get_or_insert(key, **params)
    obj.count += kwargs.get('delta', 1)
    obj.put()

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
    # added fields
    lens = ndb.StringProperty()
    crop_factor = ndb.FloatProperty(default=1.6)
    # calculated
    eqv = ndb.IntegerProperty()
    year = ndb.IntegerProperty(default=0)
    # RGB [86, 102, 102]
    rgb = ndb.IntegerProperty(repeated=True)
    # HLS names
    hue = ndb.StringProperty()
    lum = ndb.StringProperty()
    sat = ndb.StringProperty()

    def index_add(self):
        return INDEX.put(
            create_doc('%s' % self.key.urlsafe(), 
                headline=self.headline, author=self.author, body=self.model + ' ' + (self.lens or ''),
                tags=self.tags, date=self.date, url=self.get_absolute_url(), kind='Photo'))
    
    def index_del(self):
        return INDEX.delete('%s' % self.key.urlsafe())

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
        self.rgb = median(buff)
        exif = get_exif(buff)
        for field, value in exif.items():
            setattr(self, field, value)
        self.year = self.date.year
        self.hue, self.lum, self.sat = range_names(self.rgb)
        self.tags =data['tags']
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
#            TODO Not all emails are gmail
            self.author = users.User(email='%s@gmail.com' % new)
            decr_count('Photo', 'author', old.nickname())
            incr_count('Photo', 'author', self.author.nickname())
        del data['author']

        old_tags = set(self.tags)
        new_tags = set(data['tags'])
        if old_tags - new_tags:
            for name in list(old_tags-new_tags):
                decr_count('Photo', 'tags', name)
        if new_tags - old_tags:
            for name in list(new_tags-old_tags):
                incr_count('Photo', 'tags', name)
        self.tags = sorted(new_tags)
        del data['tags']

        old = self.date
        new = data['date']
        if old != new:
            decr_count('Photo', 'date', self.year)
            self.year = new.year
            incr_count('Photo', 'date', self.year)
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
            data['eqv'] = int(10*round(self.focal_length*self.crop_factor/10))

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
    
#    @ndb.transactional
    def delete(self):
        blob_info = blobstore.BlobInfo.get(self.blob_key)
        blob_info.delete()
        self.index_del()
        for name in self.tags:
            decr_count('Photo', 'tags', name)

        decr_count('Photo', 'author', self.author.nickname())
        decr_count('Photo', 'date', self.year)
        for field in PHOTO_FIELDS:
            value = getattr(self, field)
            if value:
                decr_count('Photo', field, value)

        ndb.delete_multi([x for x in ndb.Query(ancestor=self.key).iter(keys_only=True)])
        self.key.delete()

    def get_absolute_url(self):
        return webapp2.uri_for('photo', slug=self.key.string_id())

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
        return self.cached_url(240, True)

    @property
    def blob_info(self):
        return blobstore.BlobInfo.get(self.blob_key)

    @property
    def similar_url(self):
        if self.sat == 'color':
            return '/photos/hue/%s/' % self.hue
        else:
            return '/photos/lum/%s/' % self.lum

    @property
    def hex(self):
        return '#%02x%02x%02x' % tuple(self.rgb)

    @property
    def hls(self):
        rel_rgb = map(lambda x: x/255, self.rgb)
        h, l, s = colorsys.rgb_to_hls(*rel_rgb)
        return int(h*360), int(l*100), int(s*100)
    
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
    year = ndb.IntegerProperty(default=0)
    front = ndb.IntegerProperty(default=-1)
    
    def index_add(self):
        return INDEX.put(
            create_doc('%s' % self.key.urlsafe(), 
                headline=self.headline, author=self.author, body=self.summary + ' ' + self.body,
                tags=self.tags, date=self.date, url=self.get_absolute_url(), kind='Entry'))
    
    def index_del(self):
        return INDEX.delete('%s' % self.key.urlsafe())

    def _put(self):
        self.put()
        self.index_add()

    def add(self, data):
        self.headline = data['headline']
        self.summary = data['summary']
        self.date = data['date']
        self.body = data['body']
        self.tags = data['tags']

        keyname = self.key.string_id() + '_%s'
        for indx, newimage in enumerate(data['newimages']):
            if newimage['blob'] and newimage['name']:
                buff = newimage['blob'].value
                name = newimage['name']
                img = Img(parent=self.key, id=keyname % indx, num=indx, name=name, blob=buff)
                img.mime = newimage['blob'].headers['Content-Type']
                img.put_async()

        self.year=self.date.year
        self._put()

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

        keyname = self.key.string_id() + '_%s'
        for indx, obj in enumerate(data['newimages']):
            if obj['blob'] and obj['name']:
                buff = obj['blob'].value
                name = obj['name']
                img = Img(parent=self.key, id=keyname % indx, num=indx, name=name, blob=buff)
                img.mime = obj['blob'].headers['Content-Type']
                img.put_async()

        for indx, obj in enumerate(data['images']):
            if obj['delete']:
                key = ndb.Key('Entry', self.key.string_id(), 'Img', keyname % indx)
                key.delete_async()
                if indx == self.front:
                    self.front = -1

        old = self.date
        new = data['date']
        if old != new:
            decr_count('Entry', 'date', self.year)
            self.year = new.year
            incr_count('Entry', 'date', self.year)
        
        old_tags = set(self.tags)
        new_tags = set(data['tags'])
        if old_tags-new_tags:
            for name in list(old_tags-new_tags):
                decr_count('Entry', 'tags', name)
        if new_tags-old_tags:
            for name in list(new_tags-old_tags):
                incr_count('Entry', 'tags', name)
        self.tags = sorted(new_tags)

        self._put()

#    @ndb.transactional
    def delete(self):
        ndb.delete_multi_async([x for x in ndb.Query(ancestor=self.key).iter(keys_only=True)])
        self.index_del()
        decr_count('Entry', 'author', self.author.nickname())
        decr_count('Entry', 'date', self.year)
        for name in self.tags:
            decr_count('Entry', 'tags', name)

    def get_absolute_url(self):
        return webapp2.uri_for('entry', slug=self.key.string_id())

    def comment_list(self):
        return Comment.query(ancestor=self.key).order(-Comment.date)
    
    @property
    def image_list(self):
        return Img.query(ancestor=self.key).order(Img.num)
    
    def image_url(self, num):
        return '/entries/image/%s_%s' % (self.key.string_id(), num)

class Comment(ndb.Model):
    # parent Photo, Entry
    author = ndb.UserProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    year = ndb.IntegerProperty(default=0)
    forkind = ndb.StringProperty(default='Application')
    body = ndb.TextProperty(required=True)
    
    def index_add(self):
        if self.is_message:
            url = self.get_absolute_url()
            kind = 'Application'
            headline = ''
        else:
            parentobj = self.key.parent().get()
            url = parentobj.get_absolute_url()
            kind = 'Comment'
            headline = parentobj.headline
        return INDEX.put(
            create_doc('%s' % self.key.urlsafe(), 
                headline=headline, author=self.author, body=self.body, date=self.date, url=url, kind=kind))
    
    def index_del(self):
        return INDEX.delete('%s' % self.key.urlsafe())

    @property
    def is_message(self):
        return self.forkind == 'Application'

    def add(self):
        self.put()
        incr_count('Comment', 'author', self.author.nickname())
        if self.is_message:
            incr_count('Comment', 'forkind', 'Application')
        else:
            incr_count(self.key.parent().kind(), 'comment', self.key.parent().id())
            incr_count('Comment', 'forkind', self.key.parent().kind())

        self.year = self.date.year
        incr_count('Comment', 'date', self.year)
        
        self.put()
        self.index_add()
    
    def delete(self):
        decr_count('Comment', 'author', self.author.nickname())
        if self.is_message:
            decr_count('Comment', 'forkind', 'Application')
        else:
            decr_count(self.key.parent().kind(), 'comment', self.key.parent().id())
            decr_count('Comment', 'forkind', self.key.parent().kind())
        decr_count('Comment', 'date', self.year)
        self.key.delete_async()
        self.index_del()
    
    def get_absolute_url(self):
        return '%s%s' % (webapp2.uri_for('comments'), self.key.urlsafe())

class Feed(ndb.Model):
    url = ndb.StringProperty(required=True)
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty(auto_current_user_add=True)
    tags = ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty()
    
    def add(self, data):
        self.tags = data['tags']
        self.put()
        for name in self.tags:
            incr_count('Feed', 'tags', name)

    def edit(self, data):
        old_tags = set(self.tags)
        new_tags = set(data['tags'])
        if old_tags-new_tags:
            for name in list(old_tags-new_tags):
                decr_count('Feed', 'tags', name)
        if new_tags-old_tags:
            for name in list(new_tags-old_tags):
                incr_count('Feed', 'tags', name)
        self.tags = sorted(new_tags)

        self.url = data['url']
        self.headline = data['headline']
        self.put()

    def delete(self):
        for name in self.tags:
            decr_count('Feed', 'tags', name)
        slug = self.key.string_id()
        memcache.delete(slug)
        self.key.delete_async()

    def get_absolute_url(self):
        return webapp2.uri_for('feed', slug=self.key.string_id())