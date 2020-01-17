import re
import uuid
import datetime
import collections
from operator import itemgetter
from google.cloud import storage, datastore
from helpers import serialize, push_message
from config import PHOTO_FILTER, START_MSG, END_MSG

datastore_client = datastore.Client()
storage_client = storage.Client()


def all_photo_filter():
    tmp = {}
    for field in PHOTO_FILTER:
        query = datastore_client.query(kind='Counter')
        query.add_filter('forkind', '=', 'Photo')
        query.add_filter('field', '=', field)
        coll = query.fetch()
        tmp[field] = [counter for counter in coll if counter['count'] > 0]
    return tmp


def counters_values():
    result = {}
    data = all_photo_filter()
    for field in data.keys():
        _list = [counter['value'] for counter in data[field]]
        if field == 'year':
            result[field] = sorted(_list, reverse=True)
        else:
            result[field] = sorted(_list)
    return result


def counters_counts():
    """ only for Admin in console """
    result = {}
    data = all_photo_filter()
    for field in data.keys():
        _list = [{'value': counter['value'], 'count': counter['count']}
                 for counter in data[field]]
        if field == 'year':
            result[field] = sorted(
                _list, key=itemgetter('value'), reverse=True)
        else:
            result[field] = sorted(_list, key=itemgetter('value'))
    return result


def photo_count():
    query = datastore_client.query(kind='Photo')
    query.keys_only()
    return len(list(query.fetch()))


def last_entry():
    query = datastore_client.query(kind='Counter', order=['-value'])
    query.add_filter('forkind', '=', 'Photo')
    query.add_filter('field', '=', 'year')
    year_counters = [counter for counter in query.fetch()
                     if counter['count'] > 0]
    if len(year_counters) == 0:
        return {
            'safekey': None,
            'field_name': 'year',
            'name': datetime.datetime.now().year
        }
    return serialize(year_counters[0])


def results(filters, page, per_page):
    query = datastore_client.query(kind='Photo', order=['-date'])
    for pair in filters:
        query.add_filter(*pair)

    paginator = Paginator(query, per_page=per_page)
    return paginator.page(page)


class Paginator(object):
    def __init__(self, query, per_page):
        self.query = query
        self.per_page = per_page

    def page(self, token=None):
        error = None
        token = token.encode('utf-8') if token else None

        _iter = self.query.fetch(limit=self.per_page, start_cursor=token)
        _page = next(_iter.pages)  # google.api_core.page_iterator.Page object
        objects = [serialize(ent) for ent in list(_page)]

        next_cursor = _iter.next_page_token
        next_cursor = next_cursor.decode('utf-8') if next_cursor else None
        return objects, next_cursor, error


def login_user(data):
    key = datastore_client.key('User', data['uid'])
    obj = datastore_client.get(key)
    if obj is None:
        obj = datastore.Entity(key=key)

    obj['email'] = data['email']
    obj['last_login'] = datetime.datetime.now()
    datastore_client.put(obj)


def register_user(uid, token):
    key = datastore_client.key('User', uid)
    obj = datastore_client.get(key)
    obj['token'] = token
    datastore_client.put(obj)


def registrations():
    query = datastore_client.query(kind='User')
    return [ent['token'] for ent in list(query.fetch()) if ent['token']]


def rebuilder(field, token):
    counters = []
    push_message(token, START_MSG)
    query = datastore_client.query(kind='Photo', order=[field])
    iterator = query.fetch()
    if field == 'tags':
        values = [item for ent in iterator for item in ent[field]]
    else:
        values = [ent[field] for ent in iterator]

    tally = collections.Counter(values)
    for value, count in tally.items():
        id = 'Photo||{}||{}'.format(field, str(value))
        key = datastore_client.key('Counter', id)
        counter = datastore_client.get(key)
        if counter is None:
            counter = datastore.Entity(key)
        counter['count'] = count

        query = datastore_client.query(kind='Photo', order=['-date'])
        query.add_filter(field, '=', value)
        latest = list(query.fetch(3))
        if len(latest) > 0:
            counter['safekey'] = latest[0].key.to_legacy_urlsafe().decode('utf-8')

        counters.append(counter)
        push_message(token, '{} {}'.format(value, count))

    datastore_client.put_multi(counters)
    push_message(token, END_MSG)
    return tally


class Fixer(object):
    TOKEN = None
    QUERY = datastore_client.query(kind='Photo', order=['-date'])

    def run(self, batch_size=100):
        push_message(self.TOKEN, START_MSG)
        self._continue(None, batch_size)

    def _continue(self, cursor, batch_size):
        _iter = self.QUERY.fetch(limit=batch_size, start_cursor=cursor)
        _page = next(_iter.pages)  # google.api_core.page_iterator.Page object
        changed = []
        for ent in list(_page):
            filename = ent['filename'].split('/')[-1]
            ent['filename'] = '/andsnews.appspot.com/{}'.format(filename)
            changed.append(ent)

        datastore_client.put_multi(changed)
        push_message(self.TOKEN, 'saving ...')

        next_cursor = _iter.next_page_token
        if next_cursor:
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        push_message(self.TOKEN, END_MSG)
