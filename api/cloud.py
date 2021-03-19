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
    obj['last_login'] = datetime.datetime.fromtimestamp(data['lastLogin']/1000)
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
    return [ent['token'] for ent in list(query.fetch()) if 'token' in ent]


def rebuilder(field, token):
    counters = []
    push_message(token, CONFIG['start_message'])
    query = datastore_client.query(kind='Photo', order=[field])
    iterator = query.fetch()
    if field == 'tags':
        values = [item for ent in iterator for item in ent[field]]
    else:
        values = [ent[field]
                  for ent in iterator if ent[field]]

    tally = collections.Counter(values)
    for value, count in tally.items():
        id = f'Photo||{field}||{value}'
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
        push_message(token, f'{value} {count}')

    datastore_client.put_multi(counters)
    push_message(token, CONFIG['end_message'])
    return tally


def bucketInfo(param):
    key = datastore_client.key('Bucket', 'total')
    obj = datastore_client.get(key)

    def run(count=0, size=0):
        _iter = storage_client.list_blobs(BUCKET, delimiter='/')
        for blob in _iter:
            if blob.content_type == 'image/jpeg':
                count += 1
                size += blob.size
        return dict(zip(('count', 'size'), (count, size)))

    def update(obj, _new):
        obj.update(_new)
        datastore_client.put(obj)
        return dict(obj)

    if obj and param:
        if param['verb'] == 'set':
            _new = run()
            return update(obj, _new)
        elif param['verb'] in ['add', 'del'] and param['size']:
            _sign = 1 if param['verb'] == 'add' else -1
            _new = {
                'count': obj['count'] + _sign,
                'size': obj['size'] + _sign * param['size']
            }
            return update(obj, _new)
        else:  # get
            return dict(obj)
    else:
        _new = run()
        obj = datastore.Entity(key)
        return update(obj, _new)


class Repair(object):
    """
    Synchronize datastore records and Cloud bucket
    """
    TOKEN = None
    QUERY = datastore_client.query(kind='Photo')
    DATA_NAMES = []
    BLOB_NAMES = []

    def find(self, name):
        query = datastore_client.query(kind='Photo')
        query = query.add_filter('filename', '=', name)
        return list(query.fetch())

    def run(self, batch_size=1000):
        push_message(self.TOKEN, CONFIG['start_message'])

        blobs = storage_client.list_blobs(BUCKET, delimiter='/')
        self.BLOB_NAMES = [b.name for b in blobs]
        self._continue(None, batch_size)

    def _continue(self, cursor, batch_size):
        _iter = self.QUERY.fetch(limit=batch_size, start_cursor=cursor)
        _page = next(_iter.pages)
        self.DATA_NAMES.extend([ent['filename'] for ent in list(_page)])
        push_message(self.TOKEN, len(self.DATA_NAMES))

        next_cursor = _iter.next_page_token
        if next_cursor:
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        deleted = []
        B = set(self.BLOB_NAMES)
        D = set(self.DATA_NAMES)

        for name in list(B - D):
            res = self.find(name)
            if len(res) == 0:
                blob = BUCKET.get_blob(name)
                if blob:
                    deleted.append(name)
                    print(name)
                    # blob.delete()
        if (len(deleted) > 0):
            logging.error(f'{deleted} removed from bucket')
            deleted = []

        for name in list(D - B):
            blobs = storage_client.list_blobs(
                BUCKET, prefix=name, delimiter='/')
            if len(blobs.prefixes) == 0:
                res = find(name)
                deleted.append(name)
                for ent in res:
                    print(type(ent.key))
                    # datastore_client.delete(ent.key)
        if (len(deleted) > 0):
            logging.error(f'{deleted} removed from datastore')
            deleted = []

        push_message(
            self.TOKEN, f'{CONFIG["end_message"]} bucket {len(B)}, datastore {len(D)}')


class Fixer(object):
    """
    Datastore lens fix
    """
    TOKEN = None
    QUERY = datastore_client.query(
        kind='Photo').add_filter('lens', '=', 'NIKKOR Z 24-70mm f4 S')
    COUNT = 0

    def run(self, batch_size=100):
        push_message(self.TOKEN, CONFIG['start_message'])
        self._continue(None, batch_size)

    def _continue(self, cursor, batch_size):
        _iter = self.QUERY.fetch(limit=batch_size, start_cursor=cursor)
        _page = next(_iter.pages)  # google.api_core.page_iterator.Page object
        batch = []
        for ent in list(_page):
            self.COUNT += 1
            ent.update({'lens': 'Nikon NIKKOR Z 24-70mm f4 S'})
            batch.append(ent)

        if len(batch) > 0:
            datastore_client.put_multi(batch)
            push_message(self.TOKEN, f'saving {self.COUNT} ...')

        next_cursor = _iter.next_page_token
        if next_cursor:
            self._continue(next_cursor, batch_size)
        else:
            self.finish()

    def finish(self):
        push_message(self.TOKEN, CONFIG['end_message'])
