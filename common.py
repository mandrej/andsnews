from __future__ import division
import hashlib
from string import capitalize
import webapp2
from google.appengine.api import users, memcache, search
from google.appengine.ext import ndb
from wtforms import widgets, fields
from models import INDEX
from config import FAMILY, PER_PAGE, TIMEOUT


class Filter(object):
    def __init__(self, field, value):
        self.field, self.value = field, value

    @webapp2.cached_property
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
                return {self.field: capitalize(self.value)}
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


class Paginator(object):
    timeout = TIMEOUT / 6

    def __init__(self, query, per_page=PER_PAGE):
        self.query = query
        self.per_page = per_page
        self.id = hashlib.md5(repr(self.query)).hexdigest()
        self.cache = memcache.get(self.id)

        if self.cache is None:
            self.cache = [x.urlsafe() for x in self.query.fetch(keys_only=True)]
            memcache.add(self.id, self.cache, self.timeout)

    def pagekeys(self, num):
        if num < 1:
            webapp2.abort(404)

        safe_keys = self.cache[self.per_page * (num - 1): self.per_page * num + 1]
        has_next = len(safe_keys) > self.per_page
        if has_next:
            safe_keys.pop()

        return safe_keys, has_next

    def page(self, num):
        safe_keys, has_next = self.pagekeys(num)
        keys = [ndb.Key(urlsafe=safe_key) for safe_key in safe_keys]
        return ndb.get_multi(keys, use_memcache=True), has_next

    def triple(self, safe_key):
        none = ndb.Key('XXX', 'could_not_find').urlsafe()
        idx = self.cache.index(safe_key)
        page = int(1 + (idx + 1) / self.per_page)

        if idx == 0:
            if len(self.cache) == 1:
                collection = [none] + self.cache + [none]
            else:
                collection = [none] + self.cache[idx: idx + 2]
        elif idx == len(self.cache) - 1:
            collection = self.cache[idx - 1: idx + 1] + [none]
        else:
            collection = self.cache[idx - 1: idx + 2]

        try:
            keys = [ndb.Key(urlsafe=safe_key) for safe_key in collection][:3]
            prev, obj, next = ndb.get_multi(keys, use_memcache=True)
        except ValueError:
            webapp2.abort(404)
        else:
            return page, prev, obj, next


class SearchPaginator(object):
#    timeout = 60 #TIMEOUT/10
    def __init__(self, querystring, per_page=PER_PAGE):
        self.querystring = querystring
        # '"{0}"'.format(querystring.replace('"', ''))
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
        # opts = {
        #     'limit': self.per_page,
        #     'returned_fields': ['headline', 'author', 'tags', 'date', 'link', 'kind'],
        #     'returned_expressions': [
        #         search.FieldExpression(name='body', expression='snippet("%s", body)' % self.querystring)
        #     ],
        #     'snippeted_fields': ['body']
        # }
        # try:
        #     cursor = self.cache[num]
        # except KeyError:
        #     cursor = None
        #
        # opts['cursor'] = search.Cursor(web_safe_string=cursor)
        # opts['offset'] = (num - 1)*self.per_page
        # found = INDEX.search(search.Query(query_string=self.querystring,
        #                                   options=search.QueryOptions(**opts)))
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
        except search.Error, error:
            pass
        except UnicodeDecodeError, error:
            pass
        else:
            if number_found > 0:
                has_next = number_found > num * self.per_page
                # self.cache[num + 1] = found.cursor.web_safe_string
                # memcache.replace(self.id, self.cache, self.timeout)

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