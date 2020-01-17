import re
import uuid
import datetime
from PIL import Image
from io import BytesIO
from google.cloud import storage, datastore
from google.cloud.datastore.entity import Entity
from google.cloud.exceptions import GoogleCloudError, NotFound
from .config import FIREBASE, PHOTO_FILTER
from .helpers import serialize, slugify, tokenize, get_exif, Timer

datastore_client = datastore.Client()
storage_client = storage.Client()


def storage_download(safekey):
    if safekey:
        # key = datastore_client.key(kind, id)
        key = datastore.key.Key.from_legacy_urlsafe(safekey)  # TODO use id
        obj = datastore_client.get(key)
        filename = obj['filename'].split('/')[-1]  # TODO store only filename

        inp = BytesIO()
        bucket = storage_client.get_bucket(FIREBASE['storageBucket'])
        blob = bucket.get_blob(filename)
        blob.download_to_file(inp)

        return obj, inp


def update_filters(new_pairs, old_pairs):
    counters = []
    for i, (field, value) in enumerate(set(new_pairs) | set(old_pairs)):
        id = 'Photo||{}||{}'.format(field, value)
        key = datastore_client.key('Counter', id)
        counter = datastore_client.get(key)
        if counter is None:
            counter = datastore.Entity(key)
            counter['count'] = 0

        counter.update({
            'forkind': 'Photo',
            'field': field,
            'value': value
        })

        if (field, value) in old_pairs:
            counter['count'] -= 1
        if (field, value) in new_pairs:
            counter['count'] += 1
        counters.append(counter)

        query = datastore_client.query(kind='Photo', order=['-date'])
        query.add_filter(field, '=', value)

        latest = list(query.fetch(3))
        if len(latest) > 0:
            counter['safekey'] = latest[0].key.to_legacy_urlsafe().decode('utf-8')

    datastore_client.put_multi(counters)


def changed_pairs(obj):
    """
    List of changed field, value pairs
    [('year', 2017), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
    """
    pairs = []
    for field in PHOTO_FILTER:
        value = obj[field]
        if value:
            if isinstance(value, (list, tuple)):
                for v in value:
                    pairs.append((field, str(v)))
            elif isinstance(value, int):
                pairs.append((field, value))
            else:
                pairs.append((field, str(value)))  # stringify year
    return pairs


def add(fs, email):
    """
    fs: werkzeug.datastructures.FileStorage(
        stream=None, filename=None, name=None, content_type=None, content_length=None, headers=None)
    """
    # Check exist first
    filename = fs.filename
    bucket = storage_client.get_bucket(FIREBASE['storageBucket'])
    blob = bucket.get_blob(filename)
    if blob:
        filename = re.sub(
            r'\.', '-{}.'.format(str(uuid.uuid4())[:8]), filename)
    blob = bucket.blob(filename)

    _buffer = fs.read()  # === fs.stream.read()
    # Upload to storage
    try:
        with Timer() as t:
            blob.upload_from_file(
                BytesIO(_buffer), content_type=fs.content_type)
    except GoogleCloudError as e:
        return {'success': False, 'message': e.message}
    else:
        key = datastore_client.key('Photo')
        obj = datastore.Entity(key)

        exif = get_exif(_buffer)
        image_from_buffer = Image.open(BytesIO(_buffer))
        obj.update(exif)

        date = obj['date']  # from exif
        slug = slugify(filename)
        obj.update({
            'headline': filename,
            'slug': slug,
            'text': tokenize(slug),
            'filename': filename,
            'email': email,
            'nick': re.match('([^@]+)', email).group().split('.')[0],
            'tags': [],

            'date': date,
            'year': date.year,
            'month': date.month,

            'size': len(_buffer),
            'dim': list(image_from_buffer.size)
        })
        with Timer() as t:
            datastore_client.put(obj)

        new_pairs = changed_pairs(obj)
        update_filters(new_pairs, [])

        if isinstance(obj, Entity):
            return {'success': True, 'rec': serialize(obj)}
        else:
            # remove file and record
            datastore_client.delete(key)

            old_pairs = changed_pairs(obj)
            update_filters([], old_pairs)

            return {'success': False, 'message': 'Something went wrong. Picture not uploaded'}


def edit(safekey, json):
    print(json)
    key = datastore.key.Key.from_legacy_urlsafe(safekey)  # TODO use id
    obj = datastore_client.get(key)

    old_pairs = changed_pairs(obj)

    dt = json['date'].strip().split('.')[0]
    date = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
    headline = json['headline']
    slug = slugify(headline)
    email = json['email']
    obj.update({
        'headline': headline,
        'slug': slugify(headline),
        'text': tokenize(slug),
        'email': email,
        'nick': re.match('([^@]+)', email).group().split('.')[0],
        'tags': sorted(json['tags']) if 'tags' in json else [],

        'date': date,
        'year': date.year,
        'month': date.month,

        'model': json['model'] if 'model' in json else None,
        'lens': json['lens'] if 'lens' in json else None,
        'aperture': float(json['aperture']) if 'aperture' in json else None,
        'shutter': json['shutter'] if 'shutter' in json else None,
        'focal_length': round(float(json['focal_length']), 1) if 'focal_length' in json else None,
        'iso': int(json['iso']) if 'iso' in json else None
    })
    datastore_client.put(obj)

    new_pairs = changed_pairs(obj)
    update_filters(new_pairs, old_pairs)

    if isinstance(obj, Entity):
        return {'success': True, 'rec': serialize(obj)}
    else:
        return {'success': False, 'message': 'Something went wrong'}


def remove(safekey):
    key = datastore.key.Key.from_legacy_urlsafe(safekey)  # TODO use id
    obj = datastore_client.get(key)
    bucket = storage_client.get_bucket(FIREBASE['storageBucket'])
    filename = obj['filename'].split('/')[-1]  # TODO store only filename

    try:
        blob = bucket.get_blob(filename)
        blob.delete()
    except NotFound:
        return {'success': False}
    else:
        datastore_client.delete(key)

        old_pairs = changed_pairs(obj)
        update_filters([], old_pairs)
        return {'success': True}
