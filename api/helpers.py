import re
import string
import datetime
from io import BytesIO
from timeit import default_timer
from decimal import getcontext, Decimal
import firebase_admin
from firebase_admin import credentials, initialize_app, messaging

from exifread import process_file
from .config import CONFIG


def serialize(ent):
    """ google.cloud.datastore.entity """
    if ent.kind == 'Photo':
        res = dict(ent)
        res['id'] = ent.id
        res['date'] = res['date'].strftime(CONFIG['date_time_format'])
        return res


def push_message(token, message=''):
    try:
        default_app = firebase_admin.get_app()
    except ValueError as e:
        print('NEW INSTANCE')
        cred = credentials.Certificate('credentials.json')
        default_app = initialize_app(cred)

    message = messaging.Message(
        notification=messaging.Notification(title="ands", body=message),
        token=token
    )
    print(message)
    response = messaging.send(message, app=default_app)
    print(response)


def latinize(text):
    azbuka = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'ђ': 'dj',
        'е': 'e',
        'ж': 'ž',
        'з': 'z',
        'и': 'i',
        'ј': 'j',
        'к': 'k',
        'л': 'l',
        'љ': 'lj',
        'м': 'm',
        'н': 'n',
        'њ': 'nj',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'ћ': 'ć',
        'у': 'u',
        'ф': 'f',
        'х': 'h',
        'ц': 'c',
        'ч': 'č',
        'џ': 'dž',
        'ш': 'š'
    }
    # https://stackoverflow.com/a/43200929
    translator = str.maketrans('', '', string.punctuation)
    clean = text.translate(translator).lower()
    translator = str.maketrans(azbuka)
    return clean.translate(translator)


def tokenize(text):
    text = latinize(text)
    slug = '-'.join(text.split())

    res = []
    for word in slug.split('-'):
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
        'date': datetime.datetime.now()
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
            data['model'] = f'{make} {model}'

    if 'EXIF LensModel' in tags:
        # 'EXIF LensModel': (0xA434) ASCII=Nikon NIKKOR Z 24-70mm f/4 S @ 838
        data['lens'] = tags['EXIF LensModel'].printable.replace('/', '')
    if 'EXIF DateTimeOriginal' in tags:
        # 'EXIF DateTimeOriginal': (0x9003) ASCII=2020:12:03 11:28:19 @ 720
        try:
            data['date'] = datetime.datetime.strptime(
                tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
        except ValueError:
            pass
    if 'EXIF FNumber' in tags:
        getcontext().prec = 3
        data['aperture'] = float(Decimal(eval(tags['EXIF FNumber'].printable)))
    if 'EXIF ExposureTime' in tags:
        data['shutter'] = tags['EXIF ExposureTime'].printable
    if 'EXIF FocalLength' in tags:
        getcontext().prec = 3
        data['focal_length'] = float(
            Decimal(eval(tags['EXIF FocalLength'].printable)))
    if 'EXIF ISOSpeedRatings' in tags:
        getcontext().prec = 3
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
            print(f'elapsed time: {self.elapsed:.0f} ms')
