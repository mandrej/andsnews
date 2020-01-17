import re
import requests
import datetime
import unicodedata
from io import BytesIO
from timeit import default_timer
from decimal import getcontext, Decimal

from exifread import process_file
from unidecode import unidecode
from config import FIREBASE, ASA

FCM = 'https://fcm.googleapis.com/fcm/send'
HEADERS = {
    'Authorization': 'key={}'.format(FIREBASE['messagingServerKey']),
    'Content-Type': 'application/json',
}


def serialize(ent):
    """ google.cloud.datastore.entity """
    if ent.kind == 'Photo':
        return {
            'safekey': ent.key.to_legacy_urlsafe().decode('utf-8'),
            'headline': ent['headline'],
            'slug': slugify(ent['headline']),
            # 'text'
            'filename': ent['filename'].split('/')[-1],
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
            'safekey': ent['safekey'],
            'name': ent['value'],
            'field_name': ent['field']
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
    response = requests.post(FCM, json=payload, headers=HEADERS)
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


def strip_punctuation(text):
    punctuation = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
    return ''.join(x for x in text if unicodedata.category(x) not in punctuation)


def slugify(text):
    text = strip_punctuation(text)
    text = unidecode(text.lower())
    return '-'.join(text.split())


def tokenize(phrase):
    res = []
    for word in phrase.split('-'):
        for i in range(3, len(word) + 1):
            res.append(word[:i])
    return res


def get_exif(buff):
    """
    tags(details=False):

    'EXIF ApertureValue': (0x9202) Ratio=209759/62500 @ 544,
    'EXIF DateTimeDigitized': (0x9004) ASCII=2015:09:13 07:48:59 @ 516,
        'EXIF DateTimeOriginal': (0x9003) ASCII=2015:09:07 12:19:18 @ 496,
    'EXIF ExifVersion': (0x9000) Undefined=0230 @ 268,
    'EXIF ExposureBiasValue': (0x9204) Signed Ratio=-3/10 @ 552,
    'EXIF ExposureMode': (0xA402) Short=Manual Exposure @ 424,
    'EXIF ExposureProgram': (0x8822) Short=Program Normal @ 244,
        'EXIF ExposureTime': (0x829A) Ratio=1/80 @ 480,
    'EXIF Flash': (0x9209) Short=Flash did not fire @ 364,
        'EXIF FNumber': (0x829D) Ratio=16/5 @ 488,
        'EXIF FocalLength': (0x920A) Ratio=30 @ 568,
        'EXIF FocalLengthIn35mmFilm': (0xA405) Short=45 @ 448,
    'EXIF ImageUniqueID': (0xA420) ASCII=3030383036373531808E045635363034 @ 576,
        'EXIF ISOSpeedRatings': (0x8827) Short=100 @ 256,
    'EXIF MaxApertureValue': (0x9205) Ratio=97347/32767 @ 560,
    'EXIF MeteringMode': (0x9207) Short=CenterWeightedAverage @ 352,
    'EXIF SceneCaptureType': (0xA406) Short=Standard @ 460,
    'EXIF SensingMethod': (0xA217) Short=One-chip color area @ 388,
    'EXIF ShutterSpeedValue': (0x9201) Signed Ratio=790241/125000 @ 536,
    'EXIF WhiteBalance': (0xA403) Short=Auto @ 436,
    'Image DateTime': (0x0132) ASCII=2015:09:13 21:17:31 @ 190,
    'Image ExifOffset': (0x8769) Long=210 @ 102,
        'Image Make': (0x010F) ASCII=SIGMA @ 110,
        'Image Model': (0x0110) ASCII=SIGMA dp2 Quattro @ 116,
    'Image ResolutionUnit': (0x0128) Short=Pixels/Inch @ 66,
    'Image XResolution': (0x011A) Ratio=240 @ 134,
    'Image YResolution': (0x011B) Ratio=240 @ 142,
    'Thumbnail Compression': (0x0103) Short=JPEG (old-style) @ 620,
    'Thumbnail JPEGInterchangeFormat': (0x0201) Long=704 @ 668,
    'Thumbnail JPEGInterchangeFormatLength': (0x0202) Long=9699 @ 680,
    'Thumbnail ResolutionUnit': (0x0128) Short=Pixels/Inch @ 656,
    'Thumbnail XResolution': (0x011A) Ratio=72 @ 688,
    'Thumbnail YResolution': (0x011B) Ratio=72 @ 696
    """
    data = {}
    model = None
    make = None
    tags = process_file(BytesIO(buff), details=False)

    if 'Image Model' in tags:
        model = tags['Image Model'].printable.replace('/', '')

    if 'Image Make' in tags:
        make = tags['Image Make'].printable.replace('/', '')

    if model and make:
        s1 = set(make.split())
        s2 = set(model.split())
        if s1 & s2:  # contain word in make and model
            data['model'] = model
        else:
            data['model'] = '%s %s' % (make, model)
    else:
        data['model'] = 'Unknown'

    data['lens'] = tags['EXIF LensModel'].printable.replace(
        '/', '') if 'EXIF LensModel' in tags else None

    if 'EXIF DateTimeOriginal' in tags:
        data['date'] = datetime.datetime.strptime(
            tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
    else:
        data['date'] = datetime.datetime.now()

    if 'EXIF FNumber' in tags:
        getcontext().prec = 2
        data['aperture'] = float(Decimal(eval(tags['EXIF FNumber'].printable)))
    else:
        data['aperture'] = None

    data['shutter'] = tags['EXIF ExposureTime'].printable if 'EXIF ExposureTime' in tags else None

    if 'EXIF FocalLength' in tags:
        getcontext().prec = 2
        data['focal_length'] = float(
            Decimal(eval(tags['EXIF FocalLength'].printable)))
    else:
        data['focal_length'] = None

    if 'EXIF ISOSpeedRatings' in tags:
        getcontext().prec = 2
        value = int(Decimal(tags['EXIF ISOSpeedRatings'].printable) / 1)
        data['iso'] = rounding(value, ASA)
    else:
        data['iso'] = None

    # if 'GPS GPSLatitude' in tags:
    # deg_min_sec = eval(tags['GPS GPSLatitude'].printable)  # [44, 47, 559597/10000]
    # data['latitude'] = sum(map(divide60, enumerate(deg_min_sec)))  # [(0, 44), (1, 47), (2, 55.9597)]

    # if 'GPS GPSLongitude' in tags:
    #     d, m, s = eval(tags['GPS GPSLongitude'].printable)  # [20, 28, 508547/10000]
    #     data['longitude'] = d + m / 60 + s / 3600

    return data


class Timer(object):
    def __init__(self, verbose=True):
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
