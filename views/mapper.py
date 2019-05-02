import collections
import itertools
import json
import logging

import cloudstorage as gcs
import httplib2
from google.appengine.api.datastore_errors import Timeout
from google.appengine.ext import ndb, deferred
from google.appengine.runtime import DeadlineExceededError

from config import BUCKET, END_MSG, FIREBASE
from helpers import sizeof_fmt
from models import Photo, Counter, remove_doc
from cStringIO import StringIO
from PIL import Image

FCM = 'https://fcm.googleapis.com/fcm/send'
HEADERS = {
    'Authorization': 'key={}'.format(FIREBASE['messagingServerKey']),
    'Content-Type': 'application/json',
}


def push_message(token, message=''):
    """
        Firebase Cloud Messaging Server
        content: {"multicast_id":6062741259302324809,"success":1,"failure":0,"canonical_ids":0,
            "results":[{"message_id":"0:1481827534054930%2fd9afcdf9fd7ecd"}]}
    """
    payload = {
        "to": token,
        "notification": {
            "title": "ands",
            "body": message,
            "icon": "/static/manifest/icon-48x48.png"
        }
    }
    http = httplib2.Http()
    response, content = http.request(FCM, method='POST', body=json.dumps(payload), headers=HEADERS)
    # logging.error(response.status)
    # logging.error(content)


class Mapper(object):
    """ Subclasses should replace this with a model class (eg, model.Person). """
    KIND = None
    # Subclasses can replace this with a list of (property, value) tuples to filter by.
    FILTERS = []

    def __init__(self):
        self.to_put = []
        self.to_delete = []

    def map(self, entity):
        """Updates a single entity.

        Implementers should return a tuple containing two iterables (to_update, to_delete).
        """
        return [], []

    def finish(self):
        """Called when the mapper has finished, to allow for any final work to be done."""
        pass

    def get_query(self):
        """Returns a query over the specified kind, with any appropriate filters applied."""
        q = self.KIND.query()
        for prop, value in self.FILTERS:
            q = q.filter(prop == value)
        q = q.order(self.KIND._key)
        return q

    def run(self, batch_size=100):
        """Starts the mapper running."""
        self._continue(None, batch_size)

    def _batch_write(self):
        """Writes updates and deletes entities in a batch."""
        if self.to_put:
            ndb.put_multi(self.to_put)
            self.to_put = []
        if self.to_delete:
            ndb.delete_multi(self.to_delete)
            self.to_delete = []

    def _continue(self, start_key, batch_size):
        q = self.get_query()
        # If we're resuming, pick up where we left off last time.
        if start_key:
            logging.info('NEXT KEY %s' % start_key)
            key_prop = getattr(self.KIND, '_key')
            q = q.filter(key_prop > start_key)
        # Keep updating records until we run out of time.
        try:
            # Steps over the results, returning each entity and its index.
            for i, entity in enumerate(q):
                map_updates, map_deletes = self.map(entity)
                self.to_put.extend(map_updates)
                self.to_delete.extend(map_deletes)
                # Do updates and deletes in batches.
                if (i + 1) % batch_size == 0:
                    self._batch_write()
                # Record the last entity we processed.
                start_key = entity.key
            self._batch_write()
        except (Timeout, DeadlineExceededError):
            # Write any unfinished updates to the datastore.
            self._batch_write()
            # Queue a new task to pick up where we left off.
            deferred.defer(self._continue, start_key, batch_size, _queue='background')
            return
        self.finish()


class Missing(Mapper):
    TOKEN = None
    KIND = None

    def map(self, entity):
        return [entity], []

    def get_query(self):
        return self.KIND.query()

    def _batch_write(self):
        for entity in self.to_put:
            try:
                gcs.stat(entity.filename)
            except gcs.NotFoundError:
                log = '__DEL__,{},{},{},{}'.format(entity.date.isoformat(), entity.slug, entity.filename, entity.model)
                logging.info(log)
                push_message(self.TOKEN, entity.slug)
                # entity.remove()
        self.to_put = []

    def finish(self):
        push_message(self.TOKEN, END_MSG)


class Unbound(Mapper):
    """
    Remove unbound images from Google Cloud Storage
    """
    TOKEN = None
    TOTAL = 0

    def map(self, filename):
        return [], [filename]

    def run(self, batch_size=100):
        self._continue(None, batch_size)

    def _batch_write(self):
        for filename in self.to_delete:
            gcs.delete(filename)
        self.to_delete = []

    def _continue(self, marker, batch_size):
        try:
            for i, stat in enumerate(gcs.listbucket(BUCKET, max_keys=batch_size, marker=marker)):
                p = Photo.query(Photo.filename == stat.filename).get()
                if p is None:
                    map_updates, map_deletes = self.map(stat.filename)
                    self.to_put.extend(map_updates)
                    self.to_delete.extend(map_deletes)
                    self.TOTAL += stat.st_size
                    push_message(self.TOKEN, sizeof_fmt(self.TOTAL))
                if (i + 1) % batch_size == 0:
                    self._batch_write()
                marker = stat.filename
            self._batch_write()
        except (Timeout, DeadlineExceededError):
            self._batch_write()
            deferred.defer(self._continue, marker, batch_size, _queue='background')
            return
        self.finish()

    def finish(self):
        push_message(self.TOKEN, END_MSG)


class Builder(Mapper):
    TOKEN = None
    KIND = None  # ndb model
    FIELD = None
    VALUES = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        prop = self.FIELD
        values = (getattr(x, prop, None) for x in self.to_put)
        if prop == 'tags':
            values = list(itertools.chain(*values))

        self.VALUES.extend(values)
        self.to_put = []

    def finish(self):
        values = filter(None, self.VALUES)  # filter out None
        tally = collections.Counter(values)
        kind = self.KIND._class_name()
        for value, count in tally.items():
            key_name = '{}||{}||{}'.format(kind, self.FIELD, str(value))
            obj = Counter.get_or_insert(key_name, forkind=kind, field=self.FIELD, value=value)
            obj.count = count

            latest = self.KIND.latest_for(self.FIELD, value)
            if latest is not None:
                obj.repr_stamp = latest.date
                if kind == 'Photo':
                    obj.repr_url = latest.serving_url

            obj.put()
            push_message(self.TOKEN, '{} {}'.format(obj.value, obj.count))

        push_message(self.TOKEN, END_MSG)


class Fixer(Mapper):
    TOKEN = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        for entity in self.to_put:
            # 0
            remove_doc(entity.key.urlsafe())
            # 1
            entity.put()
            # 2 rebuild nick
            push_message(self.TOKEN, entity.slug)

        self.to_put = []

    def finish(self):
        push_message(self.TOKEN, END_MSG)
