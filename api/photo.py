import re
import uuid
import datetime
from PIL import Image
from io import BytesIO
from google.cloud import storage, datastore
from google.cloud.datastore.entity import Entity
from google.cloud.exceptions import GoogleCloudError, NotFound
from .config import FIREBASE, PHOTO_FILTER
from .helpers import serialize, slugify, tokenize, get_exif

datastore_client = datastore.Client()
storage_client = storage.Client()

BUCKET = storage_client.get_bucket(FIREBASE['storageBucket'])


def storage_download(filename):
    return BUCKET.get_blob(filename)


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
            counter['filename'] = latest[0]['filename']

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
    blob = BUCKET.get_blob(filename)
    if blob:
        filename = re.sub(
            r'\.', '-{}.'.format(str(uuid.uuid4())[:8]), filename)
    blob = BUCKET.blob(filename)

    _buffer = fs.read()  # === fs.stream.read()
    # Upload to storage
    try:
        blob.upload_from_file(BytesIO(_buffer), content_type=fs.content_type)
        blob.cache_control = 'public, max-age=86400'
        blob.update()
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


def edit(id, json):
    key = datastore_client.key('Photo', id)
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


def remove(id):
    key = datastore_client.key('Photo', id)
    obj = datastore_client.get(key)

    try:
        blob = BUCKET.get_blob(obj['filename'])
        blob.delete()
    except NotFound:
        return {'success': False}
    else:
        datastore_client.delete(key)

        old_pairs = changed_pairs(obj)
        update_filters([], old_pairs)
        return {'success': True}
