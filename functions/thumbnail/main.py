import logging
import google.cloud.logging
import functions_framework
from io import BytesIO
from google.cloud import storage
from PIL import Image

client = google.cloud.logging.Client()
client.setup_logging()

storage_client = storage.Client()
thumb_bucket = storage_client.get_bucket('thumbnails400')


@functions_framework.cloud_event
def make2(cloud_event):
    data = cloud_event.data
    name = data["name"]
    logging.info(f"File finalized: {name}")

    size = 400
    # skip if already exists
    thumb = thumb_bucket.get_blob(data['name'])
    if thumb:
        return

    out = BytesIO()
    source_bucket = storage_client.get_bucket(data['bucket'])
    blob = source_bucket.get_blob(data['name'])
    if blob:
        bytes = blob.download_as_bytes()
        im = Image.open(BytesIO(bytes))
        im.thumbnail((size, size), Image.BICUBIC)
        icc_profile = im.info.get('icc_profile')
        if icc_profile:
            im.save(out, im.format, icc_profile=icc_profile)
        else:
            im.save(out, im.format)

        # Upload to destination storage
        thumb = thumb_bucket.blob(data['name'])
        thumb.upload_from_string(
            out.getvalue(), content_type=data['contentType'])
        thumb.cache_control = blob.cache_control
        thumb.patch()


@functions_framework.cloud_event
def remove2(cloud_event):
    data = cloud_event.data
    name = data["name"]
    logging.info(f"File deleted: {name}")

    thumb = thumb_bucket.get_blob(data['name'])
    if thumb:
        thumb.delete()


"""
cd ~/work/andsnews/functions/thumbnail

gcloud functions deploy make2 \
--gen2 \
--runtime=python310 \
--entry-point="make2" \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=andsnews.appspot.com" \
--trigger-location="us" \
--region="us-central1"

gcloud functions deploy remove2 \
--gen2 \
--runtime=python310 \
--entry-point="remove2" \
--trigger-event-filters="type=google.cloud.storage.object.v1.deleted" \
--trigger-event-filters="bucket=andsnews.appspot.com" \
--trigger-location="us" \
--region="us-central1"
"""
