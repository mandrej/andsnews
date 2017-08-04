import collections
import itertools
import logging
import uuid

import re
import cloudstorage as gcs
from google.appengine.api.datastore_errors import Timeout
from google.appengine.ext import ndb, deferred, blobstore
from google.appengine.runtime import DeadlineExceededError

from config import BUCKET, END_MSG
from models import Counter, remove_doc
from fireapi import Firebase, push_message

FB = Firebase()


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


class RemoveIndex(Mapper):
    TOKEN = None

    def map(self, entity):
        return [entity], []

    def _batch_write(self):
        for entity in self.to_put:
            remove_doc(entity.key.urlsafe())
            push_message(self.TOKEN, entity.slug)
        self.to_put = []

    def finish(self):
        push_message(self.TOKEN, END_MSG)


# class Unbound(Mapper):
#     TOKEN = None
#
#     def map(self, entity):
#         return [entity], []
#
#     def _batch_write(self):
#         for entity in self.to_put:
#             if entity.serving_url is None:
#                 push_message(self.TOKEN, '{}'.format(entity.filename))
#                 # FB.post(path=self.CHANNEL_NAME, payload='%s' % entity.filename)
#                 # entity.remove()
#         self.to_put = []
#
#     def finish(self):
#         push_message(self.TOKEN, END_MSG)


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
            key_name = '{}||{}||{}'.format(kind, self.FIELD, str(value))
            obj = Counter.get_or_insert(key_name, forkind=kind, field=self.FIELD, value=value)
            obj.count = count

            latest = self.KIND.latest_for(self.FIELD, value)
            if latest is not None:
                obj.repr_stamp = latest.date
                if kind == 'Photo':
                    obj.repr_url = latest.async_serving_url.get_result()
                elif kind == 'Entry':
                    obj.repr_url = latest.front_img

            obj.put()
            push_message(self.TOKEN, '{} {}'.format(obj.value, obj.count))

            # FB.post(path=self.CHANNEL_NAME, payload='%s %s' % (obj.value, obj.count))

            # key = '{}'.format(hashlib.md5(str(value)).hexdigest())
            # path = '{}/{}.json'.format(self.CHANNEL_NAME, key)
            # order = 2000 - value if self.FIELD == 'date' else '{}{}'.format(PHOTO_FILTER[self.FIELD], value)
            # FB.put(path=path, payload={
            #     'order': order,
            #     'field_name': self.FIELD,
            #     'value': value,
            #     'count': count,
            #     'repr_url': repr_url,
            #     'repr_stamp': repr_stamp
            # })

        push_message(self.TOKEN, END_MSG)
        # FB.post(path=self.CHANNEL_NAME, payload='END %s' % datetime.datetime.now())
