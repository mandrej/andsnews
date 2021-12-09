
import unittest
import main
from io import BytesIO
from google.cloud import storage
from PIL import Image

storage_client = storage.Client()
# source_bucket = storage_client.get_bucket('fullsized')
thumb_bucket = storage_client.get_bucket('smallsized')
cache_control = 'public, max-age=604800'


class TestThumb(unittest.TestCase):
    def setUp(self):
        self.size = 400
        self.file = {
            'bucket': 'fullsized',
            'name': 'DSC_5839-21-12-08-198.jpg',
            'contentType': 'image/jpeg'
        }

    def test_make(self):
        out = BytesIO()
        source_bucket = storage_client.get_bucket(self.file['bucket'])
        blob = source_bucket.get_blob(self.file['name'])
        if blob:
            bytes = blob.download_as_bytes()
            im = Image.open(BytesIO(bytes))
            im.thumbnail((self.size, self.size), Image.BICUBIC)
            icc_profile = im.info.get('icc_profile')
            if icc_profile:
                im.save(out, im.format, icc_profile=icc_profile)
            else:
                im.save(out, im.format)

            # # Upload to destination storage
            thumb = thumb_bucket.blob('test_temp.jpg')
            thumb.upload_from_string(
                out.getvalue(), content_type=self.file['contentType'])
            thumb.cache_control = cache_control
            thumb.patch()

    def test_remove(self):
        # pass
        thumb = thumb_bucket.get_blob('test_temp.jpg')
        if thumb:
            thumb.delete()


# no need to run server!
# (andsnews) $ python -m unittest api/test_thumb.py
