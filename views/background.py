import logging
from mapreduce import operation as op
import cloudstorage as gcs
from google.appengine.ext import blobstore
from config import BUCKET


def indexer(entity):
    entity.index_doc()


def calculate_palette(entity):
    entity.palette_values()
    yield op.db.Put(entity)


def calculate_dimension(entity):
    entity.dim_values()
    yield op.db.Put(entity)


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
