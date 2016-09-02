from google.appengine.ext import ndb, deferred
from google.appengine.runtime import DeadlineExceededError


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
        except DeadlineExceededError:
            # Write any unfinished updates to the datastore.
            self._batch_write()
            # Queue a new task to pick up where we left off.
            deferred.defer(self._continue, start_key, batch_size)
            return
        self.finish()


class Indexer(Mapper):
    def map(self, entity):
        entity.index_doc()
        return [], []
