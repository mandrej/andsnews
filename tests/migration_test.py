import unittest
import cloudstorage as gcs
from google.appengine.ext import blobstore
from models import Photo
from config import BUCKET


class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.slug = 'sve-je-belo'

    def test_write(self):
        obj = Photo.get_by_id(self.slug)
        print obj.blob_key
        try:
            blob_info = blobstore.BlobInfo.get(obj.blob_key)  # content_type, creation, filename, size
        except blobstore.Error, err:
            print err.message
        else:
            gcs_filename = BUCKET + '/' + blob_info.filename  # /andsnews.appspot.com/SDIM4107.jpg
            write_retry_params = gcs.RetryParams(backoff_factor=1.1)
            with gcs.open(gcs_filename, 'w',
                          content_type=blob_info.content_type, retry_params=write_retry_params) as f:
                blob_reader = blobstore.BlobReader(obj.blob_key, buffer_size=1024*1024)
                buff = blob_reader.read(size=-1)
                f.write(buff)
            # /gs/andsnews.appspot.com/SDIM4107.jpg
            new_blob_key = blobstore.create_gs_key('/gs' + gcs_filename)
            # obj.put()
            print new_blob_key
