import collections
import itertools
import logging
import uuid
import httplib2
import json

import re
import cloudstorage as gcs
from google.appengine.api.datastore_errors import Timeout
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.runtime import DeadlineExceededError

from config import BUCKET, END_MSG, FIREBASE
from models import Counter, remove_doc


def push_message(token, message=''):
    """
        Firebase Cloud Messaging Server
        content: {"multicast_id":6062741259302324809,"success":1,"failure":0,"canonical_ids":0,
            "results":[{"message_id":"0:1481827534054930%2fd9afcdf9fd7ecd"}]}
    """
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': 'key={}'.format(FIREBASE['messagingServerKey']),
        'Content-Type': 'application/json',
    }
    payload = {
        "to": token,
        "notification": {
            "title": "ands",
            "body": message,
            "icon": "/images/manifest/icon-48x48.png"
        }
    }
    http = httplib2.Http()
    response, content = http.request(url, method='POST', body=json.dumps(payload), headers=headers)
    # logging.error(response.status)
    # logging.error(content)
    # return json.loads(content)


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


class Indexer(Mapper):
    TOKEN = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        for entity in self.to_put:
            entity.index_doc()
            push_message(self.TOKEN, entity.slug)
        self.to_put = []

    def finish(self):
        push_message(self.TOKEN, END_MSG)


class RemoveFields(Mapper):
    TOKEN = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        for entity in self.to_put:
            if 'repr_stamp' in entity._properties:
                del entity._properties['repr_stamp']
            if 'repr_url' in entity._properties:
                del entity._properties['repr_url']
            entity.put()
            push_message(self.TOKEN, entity.key.string_id())
        self.to_put = []

    def finish(self):
        push_message(self.TOKEN, END_MSG)


class Unbound(Mapper):
    """
    import os
    import cloudstorage as gcs
    from google.appengine.api import app_identity
    from google.appengine.ext import blobstore
    from views.models import Photo

    BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

    Remove unbound images from google cloud storage

    for s in gcs.listbucket(BUCKET, max_keys=100):
      blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + s.filename))
      p = Photo.query(Photo.blob_key == blob_key).get()
      if p is None:
        print 'delete %s' % s.filename
        gcs.delete(s.filename)

    Remove unbound images from blobstore

    for i in blobstore.BlobInfo.all():
      blob_key = i.key()
      p = Photo.query(Photo.blob_key == blob_key).get()
      if p is None:
        print 'delete %s' % i.filename
        blobstore.delete(blob_key)

    Migrate images from blobstore to google cloud storage

    import os
    import re
    import uuid
    import cloudstorage as gcs
    from google.appengine.api import app_identity
    from google.appengine.ext import blobstore
    from views.models import Photo

    BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

    for i in blobstore.BlobInfo.all():
      blob_key = i.key()
      p = Photo.query(Photo.blob_key == blob_key).get()
      object_name = BUCKET + '/' + p.slug + '.jpg'
      try:
        gcs.stat(object_name)
        object_name = BUCKET + '/' + re.sub(r'\.', '-%s.' % str(uuid.uuid4())[:8], p.slug + '.jpg')
      except gcs.NotFoundError:
        pass

      write_retry_params = gcs.RetryParams(backoff_factor=1.1)
      with gcs.open(object_name, 'w', content_type='image/jpeg', retry_params=write_retry_params) as f:
        f.write(p.buffer)
        blobstore.delete(p.blob_key)
        p.blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + object_name))
        p.filename = object_name
        p.size = f.tell()
        print '%s done.' % object_name
        p.put()
    """
    TOKEN = None

    def map(self, stat):
        return [], []

    def _batch_write(self):
        for stat in self.to_put:
            push_message(self.TOKEN, '{}'.format(stat.filename))
        self.to_put = []
        for stat in self.to_delete:
            push_message(self.TOKEN, '{}'.format(stat.filename))
        self.to_delete = []

    def _continue(self, marker, batch_size):
        stats = gcs.listbucket(BUCKET + '/', max_keys=batch_size, marker=marker)
        try:
            for i, stat in enumerate(stats):
                # map_updates, map_deletes = self.map(stat)
                if not stat.is_dir:
                    # blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + stat.filename))
                    if stat.filename is None:
                        self.to_delete.extend([stat])

                    # self.to_put.extend(map_updates)
                    # self.to_delete.extend(map_deletes)
                # Do updates and deletes in batches.
                if (i + 1) % batch_size == 0:
                    self._batch_write()
                # Record the last entity we processed.
                marker = stat.etag
            self._batch_write()
        except (Timeout, DeadlineExceededError):
            self._batch_write()
            # Queue a new task to pick up where we left off.
            deferred.defer(self._continue, marker, batch_size, _queue='background')
            return
        self.finish()

    def finish(self):
        push_message(self.TOKEN, END_MSG)


class Fixer(Mapper):
    TOKEN = None
    DATE_START = None
    DATE_END = None

    def map(self, entity):
        return [entity], []

    def get_query(self):
        return self.KIND.query(self.KIND.date < self.DATE_END, self.KIND.date >= self.DATE_START)

    def _batch_write(self):
        for entity in self.to_put:
            blob_info = blobstore.BlobInfo.get(entity.blob_key)  # content_type, creation, filename, size
            if blob_info and entity.filename is None:
                logging.info(u'{} {}'.format(blob_info.filename, blob_info.content_type))
                blob_reader = blobstore.BlobReader(entity.blob_key, buffer_size=1024 * 1024)
                buff = blob_reader.read(size=-1)
                object_name = BUCKET + '/' + blob_info.filename  # format /bucket/object
                # Check  GCS stat exist first
                try:
                    gcs.stat(object_name)
                    object_name = BUCKET + '/' + re.sub(r'\.', '-%s.' % str(uuid.uuid4())[:8], blob_info.filename)
                except gcs.NotFoundError:
                    pass

                try:
                    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
                    with gcs.open(
                        object_name,
                        'w',
                        content_type=blob_info.content_type,
                        retry_params=write_retry_params) as f:
                        f.write(buff)  # <class 'cloudstorage.storage_api.StreamingBuffer'>

                    # delete old blob key
                    blobstore.delete(entity.blob_key)
                    # write new blob key
                    entity.blob_key = blobstore.BlobKey(blobstore.create_gs_key('/gs' + object_name))
                    entity.filename = object_name
                    entity.put()

                except gcs.errors as e:
                    push_message(self.TOKEN, e.message)
                else:
                    push_message(self.TOKEN, 'DONE {}'.format(entity.slug))
            else:
                push_message(self.TOKEN, 'SKIPPED {}'.format(entity.slug))
        self.to_put = []

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
        elif prop == 'author':
            values = [x.email() for x in values]

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

            obj.put()
            push_message(self.TOKEN, '{} {}'.format(obj.value, obj.count))

        push_message(self.TOKEN, END_MSG)
