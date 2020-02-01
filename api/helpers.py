import re
import requests
import datetime
import unicodedata
from io import BytesIO
from timeit import default_timer
from decimal import getcontext, Decimal

from exifread import process_file
from unidecode import unidecode
from .config import CONFIG

HEADERS = {
    'Authorization': 'key={}'.format(CONFIG['fcm_server_key']),
    'Content-Type': 'application/json',
}


def serialize(ent):
    """ google.cloud.datastore.entity """
    if ent.kind == 'Photo':
        return {
            'id': ent.id,
            'headline': ent['headline'],
            # 'text'
            'filename': ent['filename'],
            'email': ent['email'],
            'nick': re.match('([^@]+)', ent['email']).group().split('.')[0],
            'tags': ent['tags'] if 'tags' in ent else None,

            'date': ent['date'].isoformat(),
            # 'year',
            # 'month',

            'model': ent['model'] if 'model' in ent else None,
            'lens': ent['lens'] if 'lens' in ent else None,
            'aperture': ent['aperture'] if 'aperture' in ent else None,
            'shutter': ent['shutter'] if 'shutter' in ent else None,
            'focal_length': ent['focal_length'] if 'focal_length' in ent else None,
            'iso': ent['iso'] if 'iso' in ent else None,

            # 'size',
            'dim': ent['dim'],
        }
    elif ent.kind == 'Counter':
        return {
            'field': ent['field'],
            'value': ent['value'],
            'filename': ent['filename']
        }


def push_message(token, message=''):
    """
    b'{"multicast_id":5205029634985694535,"success":0,"failure":1,"canonical_ids":0,"results":[{"error":"MismatchSenderId"}]}'

        content: {"multicast_id":6062741259302324809,"success":1,"failure":0,"canonical_ids":0,
            "results":[{"message_id":"0:1481827534054930%2fd9afcdf9fd7ecd"}]}
    """
    payload = {
        "to": token,
        "notification": {
            "title": "ands",
            "body": message
        }
    }
    response = requests.post(CONFIG['fcm_send'], json=payload, headers=HEADERS)
    j = response.json()
    if j['failure'] == 1:
        return j['results']
    else:
        return 'ok'


def rounding(val, values):
    return min(values, key=lambda x: abs(x - val))


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def tokenize(text):
    punctuation = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
    text = ''.join(x for x in text if unicodedata.category(x)
                   not in punctuation)
    text = unidecode(text.lower())
    phrase = '-'.join(text.split())

    res = []
    for word in phrase.split('-'):
        for i in range(3, len(word) + 1):
            res.append(word[:i])
    return res


def get_exif(buff):
    data = {
        'model': 'UNKNOWN',
        'lens': None,
        'date': datetime.datetime.now(),
        'aperture': None,
        'shutter': None,
        'focal_length': None,
        'iso': None,
        'dim': None
    }
    tags = process_file(BytesIO(buff), details=False)

    model = tags['Image Model'].printable.replace(
        '/', '') if 'Image Model' in tags else None
    make = tags['Image Make'].printable.replace(
        '/', '') if 'Image Make' in tags else None
    if model and make:
        s1 = set(make.split())
        s2 = set(model.split())
        if s1 & s2:  # contain word in make and model
            data['model'] = model
        else:
            data['model'] = '%s %s' % (make, model)

    if 'EXIF LensModel' in tags:
        lens = tags['EXIF LensModel'].printable
        if lens == '-- mm f/--':
            data['lens'] = None
        else:
            data['lens'] = lens.replace('/', '')
    if 'EXIF DateTimeOriginal' in tags:
        data['date'] = datetime.datetime.strptime(
            tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
    if 'EXIF FNumber' in tags:
        getcontext().prec = 2
        data['aperture'] = float(Decimal(eval(tags['EXIF FNumber'].printable)))
    if 'EXIF ExposureTime' in tags:
        data['shutter'] = tags['EXIF ExposureTime'].printable
    if 'EXIF FocalLength' in tags:
        getcontext().prec = 2
        data['focal_length'] = float(
            Decimal(eval(tags['EXIF FocalLength'].printable)))
    if 'EXIF ISOSpeedRatings' in tags:
        getcontext().prec = 2
        value = int(Decimal(tags['EXIF ISOSpeedRatings'].printable) / 1)
        data['iso'] = rounding(value, CONFIG['asa'])
    if all(['EXIF ExifImageWidth', 'EXIF ExifImageLength']) in tags:
        data['dim'] = [tags['EXIF ExifImageWidth'].printable,
                       tags['EXIF ExifImageLength'].printable]

    # for k, v in tags.items():
    #     print(k, '\t', v.printable)
    return data


class Timer(object):
    """
    with Timer() as t:
        datastore_client.put(obj)
    print(t.elapsed)
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: {0:.0f} ms'.format(self.elapsed))
