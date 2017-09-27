import unittest
import cloudstorage as gcs
from google.appengine.api import images
from google.appengine.ext import blobstore
from views.models import Photo
from views.config import BUCKET


class GCSTest(unittest.TestCase):
    def test_cloud(self):
        gcs_object_name = '/gs' + BUCKET + '/mirodjija.jpg'
        blob_key = blobstore.BlobKey(blobstore.create_gs_key(gcs_object_name))
        image_url = images.get_serving_url(blob_key)
        print blob_key  # <class 'google.appengine.api.datastore_types.BlobKey'>
        print image_url
        print '-----------------'
        # print blobstore.BlobInfo.get(blob_key)  # None
        print blobstore.FileInfo(gcs_object_name).gs_object_name  # gcs_object_name

    def test_blobstore(self):
        obj = Photo.get_by_id('mirodjija')
        image_url = images.get_serving_url(obj.blob_key)
        print obj.blob_key  # <class 'google.appengine.api.datastore_types.BlobKey'>
        print image_url
        print '-----------------'
        print blobstore.BlobInfo.get(obj.blob_key).filename  # SDIM3765.jpg

    def test_write(self):
        """ overwrite duplicate file name """
        obj = Photo.get_by_id('mirodjija')
        old_blob_key = obj.blob_key
        blob_info = blobstore.BlobInfo.get(old_blob_key)
        blob_reader = blobstore.BlobReader(old_blob_key, buffer_size=1024*1024)
        buff = blob_reader.read(size=-1)
        object_name = BUCKET + '/' + blob_info.filename  # format /bucket/object
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        with gcs.open(
            object_name,
            'w',
            content_type=blob_info.content_type,
            retry_params=write_retry_params) as f:
            f.write(buff)  # <class 'cloudstorage.storage_api.StreamingBuffer'>

        gcs_object_name = '/gs' + object_name
        obj.blob_key = blobstore.BlobKey(blobstore.create_gs_key(gcs_object_name))

        obj.put()
        blobstore.delete(old_blob_key)

        image_url = images.get_serving_url(obj.blob_key)
        print image_url
        print '-----------------'
        print blobstore.FileInfo(gcs_object_name).filename  # /gs/andsnews.appspot.com/test.jpg
