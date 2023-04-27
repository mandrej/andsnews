import string
import datetime
import requests
from timeit import default_timer

from exif import Image
from .config import CONFIG

LENSES = {
    "Nikon NIKKOR Z 24-70mm f4 S": "NIKKOR Z 24-70mm f4 S",
    "70-300 mm f4.5-5.6": "70.0-300.0 mm f4.5-5.6",
    "Canon EF-S 17-55mm f2.8 IS USM": "EF-S17-55mm f2.8 IS USM",
    "Canon EF 100mm f2.8 Macro USM": "EF100mm f2.8 Macro USM",
    "Canon EF 50mm f1.8 STM": "EF50mm f1.8 STM"
}


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


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + \
        coords[1] / 60 + \
        coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def get_exif(buff):
    data = {
        'model': 'UNKNOWN',
        'date': datetime.datetime.now()
    }
    img = Image(buff)
    if not img.has_exif:
        return data

    exif = img.get_all()
    # for k, v in exif.items():
    #     try:
    #         print(k, '\t', v)
    #     except AttributeError:
    #         pass
    # print('--------------------------------------------------------')

    tags = img.list_all()
    if all(key in tags for key in ['model', 'make']):
        model = exif['model'].replace('/', '')
        make = exif['make'].replace('/', '')
        s1 = set(make.split())
        s2 = set(model.split())
        if s1 & s2:  # contain word in make and model
            data['model'] = model
        else:
            data['model'] = f'{make} {model}'

    if 'lens_model' in tags:
        # Unify lens names
        lens = exif['lens_model'].replace('/', '')
        try:
            data['lens'] = LENSES[lens]
        except KeyError:
            data['lens'] = lens
    if 'datetime_original' in tags:  # '2023:04:24 10:13:02
        try:
            data['date'] = datetime.datetime.strptime(
                exif['datetime_original'], '%Y:%m:%d %H:%M:%S')
        except ValueError:
            pass
    if 'f_number' in tags:
        data['aperture'] = exif['f_number']
    if 'exposure_time' in tags:
        shutter = exif['exposure_time']
        if shutter <= 0.1:
            data['shutter'] = f'1/{int(1/shutter)}'
        else:
            data['shutter'] = f'{shutter}'
    if 'focal_length' in tags:
        data['focal_length'] = int(exif['focal_length'])
    if 'photographic_sensitivity' in tags:
        data['iso'] = int(exif['photographic_sensitivity'])
    if 'flash' in tags:
        data['flash'] = exif['flash'].flash_mode == 1
    if all(key in tags for key in ['gps_latitude', 'gps_latitude_ref', 'gps_longitude', 'gps_longitude_ref']):
        data['loc'] = (decimal_coords(exif['gps_latitude'], exif['gps_latitude_ref']),
                       decimal_coords(exif['gps_longitude'], exif['gps_longitude_ref']))

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
