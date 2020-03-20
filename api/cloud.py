import re
import uuid
import logging
import datetime
import collections
from operator import itemgetter
from google.cloud import storage, datastore
from .helpers import serialize, push_message
from .config import CONFIG

datastore_client = datastore.Client()
storage_client = storage.Client()

BUCKET = storage_client.get_bucket(CONFIG['firebase']['storageBucket'])


def counters_stat():
    result = {}
    for field in CONFIG['photo_filter']:
        query = datastore_client.query(kind='Counter')
        query.add_filter('forkind', '=', 'Photo')
        query.add_filter('field', '=', field)
        coll = query.fetch()

        _list = ({'value': c['value'], 'count': c['count'], 'filename': c['filename'], 'date': c['date']}
                 for c in coll if c['count'] > 0)
        if field == 'year':
            result[field] = sorted(
                _list, key=itemgetter('value'), reverse=True)
        else:
            result[field] = sorted(_list, key=itemgetter('value'))
    return result


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
    return data['uid']


def register_user(uid, token):
    key = datastore_client.key('User', uid)
    obj = datastore_client.get(key)
    if obj['token'] != token:
        obj['token'] = token
        datastore_client.put(obj)
        return True
    else:
        return False


def registrations():
    query = datastore_client.query(kind='User')
    return [ent['token'] for ent in list(query.fetch()) if ent['token']]


def rebuilder(field, token):
    counters = []
    push_message(token, CONFIG['start_message'])
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
        counter.update({
            'forkind': 'Photo',
            'field': field,
            'value': value,
            'count': count
        })

        query = datastore_client.query(kind='Photo', order=['-date'])
        query.add_filter(field, '=', value)
        latest = list(query.fetch(3))
        if len(latest) > 0:
            counter['date'] = latest[0]['date'].strftime(
                CONFIG['date_time_format'])
            counter['filename'] = latest[0]['filename']

        counters.append(counter)
        push_message(token, '{} {}'.format(value, count))

    datastore_client.put_multi(counters)
    push_message(token, CONFIG['end_message'])
    return tally


class Missing(object):
    """
    Remove datastore records with images missing in the Cloud
    """
    TOKEN = None
    QUERY = datastore_client.query(kind='Photo')
    COUNT = 0
    DELETED = []

    def run(self, batch_size=100):
        push_message(self.TOKEN, CONFIG['start_message'])
        self._continue(None, batch_size)

    def _continue(self, cursor, batch_size):
        _iter = self.QUERY.fetch(limit=batch_size, start_cursor=cursor)
        _page = next(_iter.pages)

        for ent in list(_page):
            self.COUNT += 1
            blobs = storage_client.list_blobs(
                BUCKET, prefix=ent['filename'], delimiter='/')
            for prefix in blobs.prefixes:
                if prefix == ent['filename']:
                    key = ent.key.id_or_name()
                    # datastore_client.delete(key)
                    push_message(
                        self.TOKEN, 'deleting {} ...'.format(prefix))
                    self.DELETED.append(prefix)

        next_cursor = _iter.next_page_token
        if next_cursor:
            push_message(self.TOKEN, 'checked {}, deleted {}'.format(
                self.COUNT, len(self.DELETED)))
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        logging.error(self.DELETED)
        push_message(self.TOKEN, CONFIG['end_message'])


class Unbound(object):
    """
    Remove unbound images from Google Cloud Storage
    """
    TOKEN = None
    COUNT = 0
    DELETED = []

    def run(self, batch_size=100):
        push_message(self.TOKEN, CONFIG['start_message'])
        self._continue(None, batch_size)

    def _continue(self, cursor, batch_size):
        _iter = storage_client.list_blobs(
            BUCKET, page_token=cursor, max_results=batch_size, delimiter='/')
        _page = next(_iter.pages)

        for blob in list(_page):
            if blob.content_type == 'image/jpeg':
                self.COUNT += 1
                query = datastore_client.query(kind='Photo')
                query.add_filter('filename', '=', blob.name)
                if len(list(query.fetch(1))) == 0:
                    blob.delete()
                    push_message(
                        self.TOKEN, 'deleting {} ...'.format(blob.name))
                    self.DELETED.append(blob.name)

        next_cursor = _iter.next_page_token
        if next_cursor:
            push_message(self.TOKEN, 'checked {}, deleted {}'.format(
                self.COUNT, len(self.DELETED)))
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        logging.error(self.DELETED)
        push_message(self.TOKEN, CONFIG['end_message'])


class Fixer(object):
    """
    Save all records to use <int:id> instead of <str:id_or_name>
    """
    TOKEN = None
    QUERY = datastore_client.query(kind='Photo')
    COUNT = 0

    def run(self, batch_size=100):
        push_message(self.TOKEN, CONFIG['start_message'])
        self._continue(None, batch_size)

    def _continue(self, cursor, batch_size):
        _iter = self.QUERY.fetch(limit=batch_size, start_cursor=cursor)
        _page = next(_iter.pages)  # google.api_core.page_iterator.Page object
        batch = []
        deleted = []
        for ent in list(_page):
            id_or_name = ent.key.id_or_name
            if isinstance(id_or_name, str):
                self.COUNT += 1
                key = datastore_client.key('Photo')
                obj = datastore.Entity(key)
                obj.update(ent)
                batch.append(obj)
                deleted.append(ent/key)

        if len(batch) > 0:
            datastore_client.put_multi(batch)
            datastore_client.delete_multi(deleted)
            push_message(self.TOKEN, 'saving {} ...'.format(self.COUNT))

        next_cursor = _iter.next_page_token
        if next_cursor:
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        push_message(self.TOKEN, CONFIG['end_message'])
