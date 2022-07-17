from io import BytesIO
from google.cloud import storage
from PIL import Image

storage_client = storage.Client()
thumb_bucket = storage_client.get_bucket('thumbnails400')


def makeUS(event, context):
    '''
    event:
    {'bucket': 'andsnews.appspot.com', 'contentLanguage': 'en', 'contentType': 'image/jpeg', 'crc32c': '5roF/g==',
     'etag': 'CIHo4IbxzPQCEAE=', 'generation': '1638714989622273', 'id': 'andsnews.appspot.com/DSC_5696-21-11-29-153.jpg/1638714989622273',
     'kind': 'storage#object', 'md5Hash': 'XhQvXbqrmnC69onKbbabcg==',
     'mediaLink': 'https://www.googleapis.com/download/storage/v1/b/andsnews.appspot.com/o/DSC_5696-21-11-29-153.jpg?generation=1638714989622273&alt=media',
     'metageneration': '1', 'name': 'DSC_5696-21-11-29-153.jpg', 'selfLink': 'https://www.googleapis.com/storage/v1/b/andsnews.appspot.com/o/DSC_5696-21-11-29-153.jpg',
     'size': '882556', 'storageClass': 'STANDARD', 'timeCreated': '2021-12-05T14:36:29.629Z', 'timeStorageClassUpdated': '2021-12-05T14:36:29.629Z',
     'updated': '2021-12-05T14:36:29.629Z'}
    '''
    size = 400

    # skip if already exists
    thumb = thumb_bucket.get_blob(event['name'])
    if thumb:
        return

    out = BytesIO()
    source_bucket = storage_client.get_bucket(event['bucket'])
    blob = source_bucket.get_blob(event['name'])
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
        thumb = thumb_bucket.blob(event['name'])
        thumb.upload_from_string(
            out.getvalue(), content_type=event['contentType'])
        thumb.cache_control = blob.cache_control
        thumb.patch()


def removeUS(event, context):
    thumb = thumb_bucket.get_blob(event['name'])
    if thumb:
        thumb.delete()

# gcloud functions deploy makeUS --project=andsnews --region=us-central1 --entry-point=makeUS --runtime=python310 --trigger-resource=andsnews.appspot.com --trigger-event=google.storage.object.finalize
# gcloud functions deploy removeUS --project=andsnews --region=us-central1 --entry-point=removeUS --runtime=python310 --trigger-resource=andsnews.appspot.com --trigger-event=google.storage.object.delete
