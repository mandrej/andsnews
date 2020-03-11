import re
import uuid
import logging
import datetime
from PIL import Image
from io import BytesIO
from google.cloud import storage, datastore
from google.cloud.datastore.entity import Entity
from google.cloud.exceptions import GoogleCloudError, NotFound
from .config import CONFIG
from .helpers import serialize, tokenize, get_exif

datastore_client = datastore.Client()
storage_client = storage.Client()

BUCKET = storage_client.get_bucket(CONFIG['firebase']['storageBucket'])


def storage_blob(filename):
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
            counter['date'] = latest[0]['date'].isoformat()
            counter['filename'] = latest[0]['filename']

    datastore_client.put_multi(counters)


def changed_pairs(obj):
    """
    List of changed field, value pairs
    [('year', 2017), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
    """
    pairs = []
    for field in CONFIG['photo_filter']:
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


def add(fs):
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
        blob.cache_control = CONFIG['cache_control']
        blob.update()
    except GoogleCloudError as e:
        return {'success': False, 'message': e.message}
    else:
        return {'success': True, 'rec': {
            'filename': filename,
            'size': blob.size
        }}


def update(obj, json):
    date = datetime.datetime.strptime(json['date'], '%Y-%m-%dT%H:%M:%S')
    headline = json['headline']
    email = json['email']
    loc = json['loc']
    if loc:
        if isinstance(loc, str):
            if loc.strip() == '':
                loc = None
            else:
                loc = [float(x) for x in loc.split(',')]
        elif isinstance(loc, list):
            loc = [float(x) for x in loc]

    obj.update({
        'headline': headline,
        'text': tokenize(headline),
        'filename': json['filename'],
        'email': email,
        'nick': re.match('([^@]+)', email).group().split('.')[0],
        'tags': sorted(json['tags']),

        'date': date,
        'year': date.year,
        'month': date.month,

        'model': json['model'] if json['model'] else None,
        'lens': json['lens'] if json['lens'] else None,
        'aperture': float(json['aperture']) if json['aperture'] else None,
        'shutter': json['shutter'] if json['shutter'] else None,
        'focal_length': round(float(json['focal_length']), 1) if json['focal_length'] else None,
        'iso': int(json['iso']) if json['iso'] else None,

        'size': json['size'],
        'dim': json['dim'] if json['dim'] else None,
        'loc': loc
    })
    return obj


def edit(id, json):
    if id:
        key = datastore_client.key('Photo', id)
        obj = datastore_client.get(key)
        assert obj is not None

        old_pairs = changed_pairs(obj)

        obj = update(obj, json)
        datastore_client.put(obj)

        new_pairs = changed_pairs(obj)
        update_filters(new_pairs, old_pairs)
    else:
        key = datastore_client.key('Photo')
        obj = datastore.Entity(key)

        obj = update(obj, json)
        datastore_client.put(obj)

        new_pairs = changed_pairs(obj)
        update_filters(new_pairs, [])

    if isinstance(obj, Entity):
        return {'success': True, 'rec': serialize(obj)}
    else:
        return {'success': False, 'message': 'Something went wrong'}


def removeFromBucket(filename):
    try:
        blob = BUCKET.get_blob(filename)
        blob.delete()
    except NotFound:
        return {'success': False}
    else:
        return {'success': True}


def remove(id):
    key = datastore_client.key('Photo', id)
    obj = datastore_client.get(key)
    assert obj is not None

    response = removeFromBucket(obj['filename'])
    if response['success']:
        datastore_client.delete(key)

        old_pairs = changed_pairs(obj)
        update_filters([], old_pairs)

    return response
