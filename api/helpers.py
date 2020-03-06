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
            'id': ent.key.id_or_name,
            'headline': ent['headline'],
            # 'text'
            'filename': ent['filename'] or '',
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

            'size': ent['size'],
            'dim': ent['dim'],
            'loc': ent['loc'] if 'loc' in ent else None
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


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float

    GPS GPSLatitudeRef 	 N
    GPS GPSLatitude 	 [44, 239731/5000, 0]
    GPS GPSLongitudeRef  E
    GPS GPSLongitude 	 [20, 28887999/1000000, 0]
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)


def get_exif(buff):
    data = {
        'model': 'UNKNOWN',
        'lens': None,
        'date': datetime.datetime.now(),
        'aperture': None,
        'shutter': None,
        'focal_length': None,
        'iso': None,
        'dim': None,
        'loc': None
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
        data['iso'] = int(Decimal(tags['EXIF ISOSpeedRatings'].printable) / 1)

    width = tags['EXIF ExifImageWidth'].printable if 'EXIF ExifImageWidth' in tags else None
    length = tags['EXIF ExifImageLength'].printable if 'EXIF ExifImageLength' in tags else None
    if width and length:
        data['dim'] = [int(x) for x in [width, length]]

    gps_latitude = tags.get('GPS GPSLatitude', None)
    gps_latitude_ref = tags.get('GPS GPSLatitudeRef', None)
    gps_longitude = tags.get('GPS GPSLongitude', None)
    gps_longitude_ref = tags.get('GPS GPSLongitudeRef', None)
    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

        data['loc'] = [round(x, 5) for x in [lat, lon]]
        # 'https://www.google.com/maps/search/?api=1&query={},{}'.fromat(lat, lon)

    # for k, v in tags.items():
    #     try:
    #         print(k, '\t', v.printable)
    #     except AttributeError:
    #         pass

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
