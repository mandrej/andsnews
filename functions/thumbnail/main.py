import os
import functions_framework
from io import BytesIO
from google.cloud import storage
from google.cloud.exceptions import NotFound
from PIL import Image

storage_client = storage.Client()
size = os.environ.get("MAX_SIZE", None)
thumbnails = os.environ.get("THUMBNAILS", None)


@functions_framework.cloud_event
def make2(cloud_event):
    if thumbnails is None:
        print(f"No THUMBNAILS given")
        return
    else:
        try:
            dest_bucket = storage_client.get_bucket(thumbnails)
        except NotFound:
            dest_bucket = storage_client.create_bucket(thumbnails, location="us")

    if size is None:
        print(f"No MAX_SIZE given")
        return
    else:
        max_size = int(size)

    data = cloud_event.data
    name = data["name"]

    thumb = dest_bucket.get_blob(data['name'])
    if thumb:
        print(f"Already exist: {name}")
        return

    out = BytesIO()
    source_bucket = storage_client.get_bucket(data['bucket'])
    blob = source_bucket.get_blob(data['name'])
    if blob:
        bytes = blob.download_as_bytes()
        im = Image.open(BytesIO(bytes))
        im.thumbnail((max_size, max_size), Image.BICUBIC)
        icc_profile = im.info.get('icc_profile')
        if icc_profile:
            im.save(out, im.format, icc_profile=icc_profile)
        else:
            im.save(out, im.format)

        # Upload to destination storage
        thumb = dest_bucket.blob(data['name'])
        thumb.upload_from_string(
            out.getvalue(), content_type=data['contentType'])
        thumb.cache_control = blob.cache_control
        thumb.patch()
        print(f"File finalized: {name}")


@functions_framework.cloud_event
def remove2(cloud_event):
    if thumbnails is None:
        print(f"No THUMBNAILS given")
        return
    else:
        dest_bucket = storage_client.get_bucket(thumbnails)

    data = cloud_event.data
    name = data["name"]

    thumb = dest_bucket.get_blob(data['name'])
    if thumb:
        thumb.delete()
        print(f"File deleted: {name}")
    else:
        print(f"File does not exist: {name}")


"""
cd ~/work/andsnews/functions/thumbnail

gcloud functions deploy make2 \
--gen2 \
--runtime=python310 \
--entry-point="make2" \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=andsnews.appspot.com" \
--set-env-vars="MAX_SIZE=400" \
--set-env-vars="THUMBNAILS=thumbnails400" \
--trigger-location="us" \
--region="us-central1"

gcloud functions deploy remove2 \
--gen2 \
--runtime=python310 \
--entry-point="remove2" \
--trigger-event-filters="type=google.cloud.storage.object.v1.deleted" \
--trigger-event-filters="bucket=andsnews.appspot.com" \
--set-env-vars="THUMBNAILS=thumbnails400" \
--trigger-location="us" \
--region="us-central1"
"""
