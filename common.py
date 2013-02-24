from __future__ import division

import hashlib
import itertools
import collections
from operator import itemgetter

import webapp2
from google.appengine.api import users, memcache, search
from google.appengine.ext import ndb
from wtforms import widgets, fields
from cloud import calculate_cloud
from models import INDEX, Counter, Photo
from settings import COLORS, FAMILY, PER_PAGE, TIMEOUT


def make_cloud(kind, field):
    key = '%s_%s' % (kind, field)
    content = memcache.get(key)
    if content is None:
        coll = {}
        query = Counter.query(Counter.forkind == kind, Counter.field == field)
        for counter in query:
            count = counter.count
            if count > 0:
                try:
                    # keep sorted date, eqv, iso by int
                    coll[int(counter.value)] = count
                except ValueError:
                    coll[counter.value] = count
        content = calculate_cloud(coll)
        memcache.set(key, content, TIMEOUT * 12)
    return content


def count_property(kind, field):
    prop = field
    if field == 'date':
        prop = 'year'
    key = '%s_%s' % (kind, field)
    # TODO REMEMBER
    model = ndb.Model._kind_map.get(kind)
    query = model.query()
    properties = [getattr(x, prop, None) for x in query]
    if prop == 'tags':
        properties = list(itertools.chain(*properties))
    elif prop == 'author':
        properties = [x.nickname() for x in properties]
    tally = collections.Counter(filter(None, properties))

    for value, count in tally.items():
        keyname = '%s||%s||%s' % (kind, field, value)
        params = dict(zip(('forkind', 'field', 'value'), map(str, [kind, field, value])))
        obj = Counter.get_or_insert(keyname, **params)
        if obj.count != count:
            obj.count = count
            obj.put()

    coll = dict(tally.items())
    content = calculate_cloud(coll)
    memcache.set(key, content, TIMEOUT * 12)
    return content


def count_color():
    key = 'Photo_color'
    content = memcache.get(key)
    if content is None:
        content = []
        for k, d in COLORS.items():
            query = Photo.query(Photo.color == d['name']).order(-Photo.date)
            data = COLORS[k]
            data.update({'count': query.count(1000)})
            content.append(data)
        content = sorted(content, key=itemgetter('order'))
        memcache.set(key, content, TIMEOUT * 12)
    return content


def get_or_build(key):
    kind, field = key.split('_')
    items = memcache.get(key)
    if items is None:
        if field == 'color':
            items = count_color()
        else:
            items = make_cloud(kind, field)

    if field != 'color':
        # 10 most frequent
        items = sorted(items, key=itemgetter('count'), reverse=True)[:10]
    return items


class Filter:
    def __init__(self, field, value):
        self.field, self.value = field, value

    @property
    def parameters(self):
        try:
            assert (self.field and self.value)
        except AssertionError:
            return {}
        else:
            if self.field == 'date':
                return {'year': int(self.value)}
            elif self.field == 'author':
                # TODO Not all emails are gmail
                return {self.field: users.User(email='%s@gmail.com' % self.value)}
            elif self.field == 'forkind':
                return {self.field: self.value.capitalize()}
            elif self.field == 'hue':
                return {self.field: self.value, 'sat': 'color'}
            elif self.field == 'lum':
                return {self.field: self.value, 'sat': 'monochrome'}
            else:
                try:
                    self.value = int(self.value)
                except ValueError:
                    pass
                return {'%s' % self.field: self.value}


class Paginator:
    timeout = TIMEOUT / 6

    def __init__(self, query, per_page=PER_PAGE):
        self.query = query
        self.per_page = per_page
        self.id = hashlib.md5(repr(self.query)).hexdigest()
        self.cache = memcache.get(self.id)

        if self.cache is None:
            self.cache = {0: None}
            memcache.add(self.id, self.cache, self.timeout)

    def pagekeys(self, num):
        if num < 1: webapp2.abort(404)

        try:
            cursor = self.cache[num - 1]
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, start_cursor=cursor)
        except KeyError:
            offset = (num - 1) * self.per_page
            keys, cursor, has_next = self.query.fetch_page(self.per_page, keys_only=True, offset=offset)

        if not keys:
            return keys, False

        if keys and cursor:
            self.cache[num] = cursor
            memcache.replace(self.id, self.cache, self.timeout)
            return keys, has_next
        else:
            webapp2.abort(404)

    def page(self, num):
        keys, has_next = self.pagekeys(num)
        return ndb.get_multi(keys), has_next

    def triple(self, idx):
        """ num and idx are 1 base index """
        none = ndb.Key('XXX', 'xxx')
        rem = idx % self.per_page
        num = int(idx / self.per_page) + (0 if rem == 0 else 1)
        keys, has_next = self.pagekeys(num)

        if rem == 1:
            if num == 1:
                collection = [none] + keys + [none]
            else:
                other, x = self.pagekeys(num - 1)
                collection = (other + keys + [none])[idx - (num - 2) * self.per_page - 2:]
        else:
            if has_next:
                other, x = self.pagekeys(num + 1)
            else:
                other = [none]
            collection = (keys + other)[idx - (num - 1) * self.per_page - 2:]

        prev, obj, next = ndb.get_multi(collection[:3])
        return num, prev, obj, next


class SearchPaginator:
#    timeout = 60 #TIMEOUT/10
    def __init__(self, querystring, per_page=PER_PAGE):
        self.querystring = querystring
        # '"{0}"'.format(querystring.replace('"',''))
        self.per_page = per_page

    #        self.id = hashlib.md5(querystring).hexdigest()
    #        self.cache = memcache.get(self.id)
    #
    #        if self.cache is None:
    #            self.cache = {1: None}
    #            memcache.add(self.id, self.cache, self.timeout)

    def page(self, num):
        error = None
        results = []
        number_found = 0
        has_next = False
        #        opts = {
        #            'limit': self.per_page,
        #            'returned_fields': ['headline', 'author', 'tags', 'date', 'link', 'kind'],
        #            'returned_expressions': [search.FieldExpression(name='body', expression='snippet("%s", body)' % self.querystring)]
        #            'snippeted_fields': ['body']
        #        }
        #        try:
        #            cursor = self.cache[num]
        #        except KeyError:
        #            cursor = None
        #
        #        opts['cursor'] = search.Cursor(web_safe_string=cursor)
        #        opts['offset'] = (num - 1)*self.per_page
        #        found = INDEX.search(search.Query(query_string=self.querystring,
        #                                          options=search.QueryOptions(**opts)))
        query = search.Query(
            query_string=self.querystring,
            options=search.QueryOptions(
                limit=self.per_page,
                offset=(num - 1) * self.per_page,
                returned_fields=['headline', 'author', 'tags', 'date', 'link', 'kind'],
                snippeted_fields=['body']
            ))
        try:
            found = INDEX.search(query)
            results = found.results
            number_found = found.number_found
        except Exception, error:
            found = []
        else:
            if number_found > 0:
                has_next = number_found > num * self.per_page
                #            self.cache[num + 1] = found.cursor.web_safe_string
                #            memcache.replace(self.id, self.cache, self.timeout)

        return results, number_found, has_next, error


class EmailField(fields.SelectField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)
        user = users.get_current_user()
        email = user.email()
        if not email in FAMILY:
            FAMILY.append(email)
        self.choices = [(users.User(x).nickname(), x) for x in FAMILY]


class TagsField(fields.TextField):
    widget = widgets.TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = sorted([x.strip().lower() for x in valuelist[0].split(',') if x.strip() != ''])
        else:
            self.data = []