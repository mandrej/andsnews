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
    try:
        blob_info = blobstore.BlobInfo.get(entity.blob_key)  # content_type, creation, filename, size
    except blobstore.Error, err:
        logging.error(err.message)
    else:
        gcs_filename = BUCKET + '/' + blob_info.filename  # /andsnews.appspot.com/SDIM4107.jpg
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        with gcs.open(gcs_filename, 'w',
                      content_type=blob_info.content_type, retry_params=write_retry_params) as f:
            blob_reader = blobstore.BlobReader(entity.blob_key, buffer_size=1024*1024)
            buff = blob_reader.read(size=-1)
            f.write(buff)
        # /gs/andsnews.appspot.com/SDIM4107.jpg
        entity.blob_key = blobstore.create_gs_key('/gs' + gcs_filename)
        yield op.db.Put(entity)
