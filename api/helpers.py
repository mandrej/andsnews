import string
import datetime
import requests
from io import BytesIO
from timeit import default_timer
from decimal import getcontext, Decimal

from exifread import process_file
from .config import CONFIG


def push_message(recipients, message='', **data):
    """
    Cloud function send
    """
    body = {"recipients": recipients, "message": message}
    if data:
        body["data"] = data

    response = requests.post(CONFIG['message_url'], json=body, headers={
                             'Content-Type': 'application/json'})
    return response.content


def serialize(ent):
    """ google.cloud.datastore.entity """
    if ent.kind == 'Photo':
        res = dict(ent)
        res['id'] = ent.id
        res['date'] = res['date'].strftime(CONFIG['date_time_format'])
        return res


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


def ratio_to_dms(dms_ratio):
    def frac_to_dec(ratio):
        return float(ratio.num) / float(ratio.den)

    return frac_to_dec(dms_ratio[0]) + (frac_to_dec(dms_ratio[1])/60.0) + (frac_to_dec(dms_ratio[2])/3600.0)


def get_exif(buff):
    data = {
        'model': 'UNKNOWN',
        'date': datetime.datetime.now()
    }
    tags = process_file(BytesIO(buff), details=False)

    # for k, v in tags.items():
    #     try:
    #         print(k, '\t', v.printable)
    #     except AttributeError:
    #         pass
    # print('--------------------------------------------------------')

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
    if 'EXIF Flash' in tags:
        # Flash fired, compulsory flash mode, return light detected / Flash did not fire
        data['flash'] = tags['EXIF Flash'].printable.find('Flash fired') >= 0

    # FIXME LightRoom NO EXIF ExifImageWidth, EXIF ExifImageLength
    # width = tags['EXIF ExifImageWidth'].printable if 'EXIF ExifImageWidth' in tags else None
    # length = tags['EXIF ExifImageLength'].printable if 'EXIF ExifImageLength' in tags else None
    # if width and length:
    #     data['dim'] = [int(x) for x in [width, length]]

    # https://www.programcreek.com/python/?code=Sotera%2Fpst-extraction%2Fpst-extraction-master%2Fspark%2Fimage_exif_processing.py
    # 'https://www.google.com/maps/search/?api=1&query={},{}'.fromat(lat, lon)
    gps = {'lat': 0.0, 'lon': 0.0}
    if 'GPS GPSLatitudeRef' in tags:
        gps["latref"] = tags['GPS GPSLatitudeRef'].printable  # N
    if 'GPS GPSLongitudeRef' in tags:
        gps["lonref"] = tags['GPS GPSLongitudeRef'].printable  # E
    if 'GPS GPSLatitude' in tags and gps["latref"] != '':
        gps["lat"] = (1 if "latref" in gps and gps["latref"] == "N" else -1) * \
            ratio_to_dms(
                tags["GPS GPSLatitude"].values)  # [44, 239731/5000, 0]
    if "GPS GPSLongitude" in tags and gps["lonref"] != '':
        gps["lon"] = (1 if "lonref" in gps and gps["lonref"] == "E" else -1) * \
            ratio_to_dms(
                tags["GPS GPSLongitude"].values)  # [20, 28887999/1000000, 0]

    if gps["lat"] != 0.0 or gps["lon"] != 0.0:
        data['loc'] = [round(x, 5) for x in [gps["lat"], gps["lon"]]]

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
