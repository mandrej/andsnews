import re
import json
import uuid
import logging
import itertools
import collections
import cloudstorage as gcs
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.api import channel
from google.appengine.api.datastore_errors import Timeout
from google.appengine.runtime import DeadlineExceededError
from models import Counter
from config import BUCKET


class Mapper(object):
    # Subclasses should replace this with a model class (eg, model.Person).
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
    CHANNEL_NAME = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        for entity in self.to_put:
            entity.index_doc()
            channel.send_message(self.CHANNEL_NAME, json.dumps({'message': '%s' % entity.slug}))
        self.to_put = []

    def finish(self):
        channel.send_message(self.CHANNEL_NAME, json.dumps({'message': 'END'}))


class Fixer(Mapper):
    CHANNEL_NAME = None
    DATE_LESS_THEN = None

    def map(self, entity):
        return [entity], []

    def get_query(self):
        """Returns a query over the specified kind, with any appropriate filters applied."""
        q = self.KIND.query(self.KIND.date < self.DATE_LESS_THEN)
        return q

    def _batch_write(self):
        for entity in self.to_put:
            blob_info = blobstore.BlobInfo.get(entity.blob_key)  # content_type, creation, filename, size
            if blob_info is not None:
                channel.send_message(self.CHANNEL_NAME, json.dumps({'message': '%s' % blob_info.filename}))
                # blob_reader = blobstore.BlobReader(entity.blob_key, buffer_size=1024 * 1024)
                # buff = blob_reader.read(size=-1)
                # object_name = BUCKET + blob_info.filename  # format /bucket/object
                #
                # # Check  GCS stat exist first
                # try:
                #     gcs.stat(object_name)
                #     object_name = BUCKET + '/' + re.sub(r'\.', '-%s.' % str(uuid.uuid4())[:8], blob_info.filename)
                # except gcs.NotFoundError:
                #     pass
                #
                # write_retry_params = gcs.RetryParams(backoff_factor=1.1)
                # with gcs.open(
                #         object_name,
                #         'w',
                #         content_type=blob_info.content_type,
                #         retry_params=write_retry_params) as f:
                #     f.write(buff)  # <class 'cloudstorage.storage_api.StreamingBuffer'>
                #
                # gcs_object_name = '/gs' + object_name
                # entity.blob_key = blobstore.BlobKey(blobstore.create_gs_key(gcs_object_name))
                # entity.put()

            # channel.send_message(self.CHANNEL_NAME, json.dumps({'message': '%s' % entity.slug}))
        self.to_put = []

    def finish(self):
        channel.send_message(self.CHANNEL_NAME, json.dumps({'message': 'END'}))


class Builder(Mapper):
    FIELD = None
    VALUES = None
    CHANNEL_NAME = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        prop = self.FIELD
        if self.FIELD == 'date':
            prop = 'year'

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
            args = (kind, self.FIELD, str(value))  # stringify year
            key_name = '%s||%s||%s' % args
            params = dict(zip(('forkind', 'field', 'value'), args))
            obj = Counter.get_or_insert(key_name, **params)

            latest = self.KIND.latest_for(obj.field, obj.value)
            if latest is not None:
                if obj.forkind == 'Photo':
                    obj.repr_url = latest.serving_url
                elif obj.forkind == 'Entry':
                    obj.repr_url = latest.front_img

                obj.repr_stamp = latest.date

            obj.count = count
            obj.put()

            channel.send_message(self.CHANNEL_NAME, json.dumps({'message': '%s %s' % (value, count)}))
        channel.send_message(self.CHANNEL_NAME, json.dumps({'message': 'END'}))


def current_fix(entity):
    blob_info = blobstore.BlobInfo.get(entity.blob_key)  # content_type, creation, filename, size
    if blob_info is not None:
        blob_reader = blobstore.BlobReader(entity.blob_key, buffer_size=1024*1024)
        buff = blob_reader.read(size=-1)
        object_name = BUCKET + blob_info.filename  # format /bucket/object
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        with gcs.open(
            object_name,
            'w',
            content_type=blob_info.content_type,
            retry_params=write_retry_params) as f:
            f.write(buff)  # <class 'cloudstorage.storage_api.StreamingBuffer'>

        gcs_object_name = '/gs' + object_name
        entity.blob_key = blobstore.BlobKey(blobstore.create_gs_key(gcs_object_name))
        yield op.db.Put(entity)
