import logging
import datetime
import collections
from google.cloud import datastore
from .photo import datastore, datastore_client, storage_client, BUCKET
from .helpers import serialize, push_message
from .config import CONFIG


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
        id = F'Photo||{field}||{value}'
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
        push_message(token, F'{value} {count}')

    datastore_client.put_multi(counters)
    push_message(token, CONFIG['end_message'])
    return tally


def bucketInfo(read=True):
    key = datastore_client.key('Bucket', 'total')
    obj = datastore_client.get(key)

    def run(count=0, size=0):
        _iter = storage_client.list_blobs(BUCKET, delimiter='/')
        for blob in _iter:
            if blob.content_type == 'image/jpeg':
                count += 1
                size += blob.size
        return dict(zip(('count', 'size'), (count, size)))

    if obj:
        if read:
            return dict(obj)
        else:
            _new = run()
            obj.update(_new)
            datastore_client.put(obj)
            return dict(obj)
    else:
        _new = run()
        obj = datastore.Entity(key)
        obj.update(_new)
        datastore_client.put(obj)
        return dict(obj)


class Missing(object):
    """
    Remove datastore records with images missing in the Cloud (404)
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
                    push_message(
                        self.TOKEN, F'deleting {prefix} ...')
                    self.DELETED.append(prefix)
                    datastore_client.delete(key)

        next_cursor = _iter.next_page_token
        if next_cursor:
            push_message(
                self.TOKEN, F'checked {self.COUNT}, deleted {len(self.DELETED)}')
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        logging.error(self.DELETED)
        push_message(self.TOKEN, CONFIG['end_message'])


class Unbound(object):
    """
    Remove images from the Cloud not referenced in datastore (SLOW)
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
                    push_message(
                        self.TOKEN, F'deleting {blob.name} ...')
                    self.DELETED.append(blob.name)
                    blob.delete()

        next_cursor = _iter.next_page_token
        if next_cursor:
            push_message(
                self.TOKEN, F'checked {self.COUNT}, deleted {len(self.DELETED)}')
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
            push_message(self.TOKEN, F'saving {self.COUNT} ...')

        next_cursor = _iter.next_page_token
        if next_cursor:
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        push_message(self.TOKEN, CONFIG['end_message'])
