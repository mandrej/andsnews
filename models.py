from __future__ import division
import colorsys
from google.appengine.ext import ndb, deferred
from google.appengine.api import images, users, memcache, search

INDEX = search.Index(name='searchindex')
KEYS = ['Photo_tags', 'Photo_author', 'Photo_date', 
        'Photo_model', 'Photo_lens', 'Photo_eqv', 'Photo_iso', 'Photo_colors', 
        'Entry_tags', 'Entry_author', 'Entry_date',
        'Feed_tags',
        'Comment_forkind', 'Comment_author', 'Comment_date']
PHOTO_FIELDS = ('model', 'lens', 'eqv', 'iso',)
ENTRY_IMAGES = 10

HUE = [
    {'span': map(lambda x: x+360 if x<0 else x, xrange(-10, 10)), 'order': '0', 'name': 'red', 'hex': '#cc0000'}, # 0
    {'span': xrange(10, 40), 'order': '1', 'name': 'orange', 'hex': '#ff7f00'}, # 30
    {'span': xrange(40, 60), 'order': '2', 'name': 'yellow', 'hex': '#ffff0f'}, # 60
    {'span': xrange(60, 150), 'order': '3', 'name': 'green', 'hex': '#00bf00'}, # 120
    {'span': xrange(150, 190), 'order': '4', 'name': 'teal', 'hex': '#00bfbf'}, # 180
    {'span': xrange(190, 240), 'order': '5', 'name': 'blue', 'hex': '#005fbf'}, # 210
    {'span': xrange(240, 290), 'order': '6', 'name': 'purple', 'hex': '#5f00bf'}, # 270
    {'span': xrange(290, 350), 'order': '7', 'name': 'pink', 'hex': '#bf005f'} # 330
]
LUM = [
    {'span': xrange(0, 10), 'order': '8', 'name': 'dark', 'hex': '#191919'},
    {'span': xrange(10, 40), 'order': '9', 'name': 'medium', 'hex': '#4c4c4c'},
    {'span': xrange(40, 101), 'order': 'a', 'name': 'light', 'hex': '#cccccc'}
]
SAT = [
    {'span': xrange(0, 10), 'name': 'monochrome'},
    {'span': xrange(10, 101), 'name': 'color'}
]

def range_names(h, l, s):
    def in_range(value, component):
        for x in component:
            if value in x['span']:
                return x['name']
    
    hue = in_range(h, HUE)
    lum = in_range(l, LUM)
    sat = in_range(s, SAT)
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
    ])

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

class Picture(ndb.Model):
    # parent Photo
    width = ndb.IntegerProperty()
    height = ndb.IntegerProperty()
    size = ndb.IntegerProperty()
    blob = ndb.BlobProperty(default=None)
    small = ndb.BlobProperty(default=None)
    # RGB [86, 102, 102]
    rgb = ndb.IntegerProperty(repeated=True)

    @property
    def hex(self):
        return '#%02x%02x%02x' % tuple(self.rgb)
    
    def rel_rgb(self):
        return map(lambda x: x/255, self.rgb)

    @property
    def hls(self):
        h, l, s = colorsys.rgb_to_hls(*self.rel_rgb())
        return int(h*360), int(l*100), int(s*100)

    @property
    def hsv(self):
        h, s, v = colorsys.rgb_to_hsv(*self.rel_rgb())
        return int(h*360), int(s*100), int(v*100)
    
class Photo(ndb.Model):
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty(auto_current_user_add=True)
    tags = ndb.StringProperty(repeated=True)
    # EXIF data
    model = ndb.StringProperty()
    aperture = ndb.FloatProperty()
    shutter = ndb.StringProperty()
    focal_length = ndb.FloatProperty()
    iso = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()
    program = ndb.StringProperty()
    # added fields
    lens = ndb.StringProperty()
    crop_factor = ndb.FloatProperty(default=1.6)
    # calculated
    eqv = ndb.IntegerProperty()
    year = ndb.IntegerProperty(default=0)
    month = ndb.IntegerProperty(default=0)
    # HLS names
    hue = ndb.StringProperty()
    lum = ndb.StringProperty()
    sat = ndb.StringProperty()
    # landscape|portrait
    aspect = ndb.StringProperty()
    
    def index_add(self):
        return INDEX.put(
            create_doc('%s' % self.key.urlsafe(), 
                headline=self.headline, author=self.author, body=self.model + ' ' + (self.lens or ''), tags=self.tags, date=self.date, url=self.get_absolute_url(), kind='Photo'))
    
    def index_del(self):
        return INDEX.delete('%s' % self.key.urlsafe())

    @property
    def picture(self):
        return Picture.query(ancestor = self.key)

    def _put(self):
        super(Photo, self).put()
        self.index_add()

    def _add(self, data, buff, exif):
        img = images.Image(buff)
        pic = Picture(parent=self.key, id=self.key.string_id(), blob=buff)
        pic.width, pic.height, pic.size = img.width, img.height, len(buff)
        self.aspect = 'landscape' if (pic.width >= pic.height) else 'portrait'
        pic.put_async()

        for field, value in exif.items():
            setattr(self, field, value)
        self.year = self.date.year
        self.month = self.date.month

        self.tags = sorted([x.strip().lower() for x in data['tags'].split(',') if x.strip() != ''])
        self._put()

    def add(self, data, buff, exif):
        ndb.transaction(lambda: self._add(data, buff, exif))
        for name in self.tags:
            incr_count('Photo', 'tags', name)
        incr_count('Photo', 'author', self.author.nickname())
        incr_count('Photo', 'date', self.year)
        for field in PHOTO_FIELDS:
            value = exif.get(field, None)
            if value:
                incr_count('Photo', field, value)

    def edit(self, data, buff, exif):
        old = self.author
        new = data['author']
        if new != old.email():
            self.author = users.User(new)
            decr_count('Photo', 'author', old.nickname())
            incr_count('Photo', 'author', self.author.nickname())

        self.headline = data['headline']

        if buff:
            img = images.Image(buff)
            pic = self.picture.get()
            pic.blob = buff
            pic.small = None
            pic.width, pic.height, pic.size = img.width, img.height, len(buff)
            self.aspect = 'landscape' if (pic.width >= pic.height) else 'portrait'
            pic.put()
        
        for field, value in exif.items():
            if field in PHOTO_FIELDS:
                old = getattr(self, field)
                new = exif.get(field)
                if old != new:
                    if old:
                        decr_count('Photo', field, old)
                    if new:
                        incr_count('Photo', field, new)
                    setattr(self, field, new)
            else:
                setattr(self, field, value)

        old_tags = set(self.tags)
        new_tags = set([x.strip().lower() for x in data['tags'].split(',') if x.strip() != ''])
        if old_tags-new_tags:
            for name in list(old_tags-new_tags):
                decr_count('Photo', 'tags', name)
        if new_tags-old_tags:
            for name in list(new_tags-old_tags):
                incr_count('Photo', 'tags', name)
        self.tags = sorted(new_tags)
        
        old = self.date
        new = data['date']
        if old != new:
            decr_count('Photo', 'date', self.year)
            self.year = new.year
            self.month = new.month
            incr_count('Photo', 'date', self.year)
        
        self._put()
    
    @ndb.transactional
    def delete(self):
        ndb.delete_multi_async([x for x in ndb.Query(ancestor=self.key).iter(keys_only=True)])
        self.index_del()
        for name in self.tags:
            decr_count('Photo', 'tags', name)

        decr_count('Photo', 'author', self.author.nickname())
        decr_count('Photo', 'date', self.year)
        for field in PHOTO_FIELDS:
            value = getattr(self, field)
            if value:
                decr_count('Photo', field, value)

    def get_absolute_url(self):
        return '/photos/%s' % self.key.string_id()
    
    def similar_url(self):
        if self.sat == 'color':
            return '/photos/hue/%s' % self.hue
        else:
            return '/photos/lum/%s' % self.lum
    
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
    month = ndb.IntegerProperty(default=0)
    front = ndb.IntegerProperty(default=-1)
    
    def index_add(self):
        return INDEX.put(
            create_doc('%s' % self.key.urlsafe(), 
                headline=self.headline, author=self.author, body=self.summary + ' ' + self.body, tags=self.tags, date=self.date, url=self.get_absolute_url(), kind='Entry'))
    
    def index_del(self):
        return INDEX.delete('%s' % self.key.urlsafe())

    def _put(self):
        super(Entry, self).put()
        self.index_add()

    def _add(self, data):
        i = 0
        keyname = self.key.string_id() + '_%s'
        for _dict in data.get('images', []):
            if 'blob' in _dict and 'name' in _dict:
                buff = _dict['blob'].read()
                img = Img(parent=self.key, id=keyname % i, num=i,
                          name=_dict['name'], blob=buff)
                img.mime = _dict['blob'].content_type
                img.put_async()
            i += 1
        
        self.date = data['date']
        self.year=self.date.year
        self.month=self.date.month
        
        self.tags = sorted([x.strip().lower() for x in data['tags'].split(',') if x.strip() != ''])
        self._put()

    def add(self, data):
        ndb.transaction(lambda: self._add(data))
        incr_count('Entry', 'author', self.author.nickname())
        incr_count('Entry', 'date', self.year)
        for name in self.tags:
            incr_count('Entry', 'tags', name)

    def edit(self, data):
        self.headline = data['headline']
        self.summary = data['summary']
        self.date = data['date']
        self.body = data['body']

        i = 0
        self.front = int(data['front'])
        keyname = self.key.string_id() + '_%s'
        for _dict in data.get('images', []):
            if _dict['ORDER'] is not None:
                obj = Img.get_by_id(keyname % _dict['ORDER'], self.key)
                if _dict['DELETE']:
                    if i == self.front:
                        self.front = -1
                    obj.key.delete_async()
                else:
                    if _dict['blob'] is not None:
                        buff = _dict['blob'].read()
                        obj.mime = _dict['blob'].content_type
                        obj.blob = buff
                        obj.small = None
                    if _dict['name'] is not None:
                        if obj.name != _dict['name']:
                            obj.name = _dict['name']
                    obj.put()
            else:
                if _dict['blob'] and _dict['name']:
                    buff = _dict['blob'].read()
                    img = Img(parent=self, id=keyname % i, num=i,
                              name=_dict['name'], blob=buff)
                    img.mime = _dict['blob'].content_type
                    img.put()
            i += 1
        
        old = self.date
        new = data['date']
        if old != new:
            decr_count('Entry', 'date', self.year)
            self.year = new.year
            self.month = new.month
            incr_count('Entry', 'date', self.year)
        
        old_tags = set(self.tags)
        new_tags = set([x.strip().lower() for x in data['tags'].split(',') if x.strip() != ''])
        if old_tags-new_tags:
            for name in list(old_tags-new_tags):
                decr_count('Entry', 'tags', name)
        if new_tags-old_tags:
            for name in list(new_tags-old_tags):
                incr_count('Entry', 'tags', name)
        self.tags = sorted(new_tags)

        self._put()

    @ndb.transactional
    def delete(self):
        ndb.delete_multi_async([x for x in ndb.Query(ancestor=self.key).iter(keys_only=True)])
        self.index_del()
        decr_count('Entry', 'author', self.author.nickname())
        decr_count('Entry', 'date', self.year)
        for name in self.tags:
            decr_count('Entry', 'tags', name)

    def get_absolute_url(self):
        return '/entries/%s' % self.key.string_id()

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
    month = ndb.IntegerProperty(default=0)
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
        self.month = self.date.month
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
        return '/comments/%s' % self.key.urlsafe()

class Feed(ndb.Model):
    url = ndb.StringProperty(required=True)
    headline = ndb.StringProperty(required=True)
    author = ndb.UserProperty(auto_current_user_add=True)
    tags = ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty()
    
    def _put(self):
        super(Feed, self).put()

    def _add(self, data):
        self.tags = sorted([x.strip().lower() for x in data['tags'].split(',') if x.strip() != ''])
        self._put()

    def add(self, data):
        ndb.transaction(lambda: self._add(data))
        for name in self.tags:
            incr_count('Feed', 'tags', name)

    def edit(self, data):
        old_tags = set(self.tags)
        new_tags = set([x.strip().lower() for x in data['tags'].split(',') if x.strip() != ''])
        if old_tags-new_tags:
            for name in list(old_tags-new_tags):
                decr_count('Feed', 'tags', name)
        if new_tags-old_tags:
            for name in list(new_tags-old_tags):
                incr_count('Feed', 'tags', name)
        self.tags = sorted(new_tags)

        self.url = data['url']
        self.headline = data['headline']
        self._put()

    def delete(self):
        for name in self.tags:
            decr_count('Feed', 'tags', name)
        slug = self.key().name()
        memcache.delete(slug)
        super(Feed, self).delete()

    def get_absolute_url(self):
        return '/news/%s' % self.key.string_id()

    def has_cache(self):
        return memcache.get(self.key.string_id()) is not None
