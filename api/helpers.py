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
    """
    '_segments', 'delete', 'delete_all', 'get', 'get_all', 'get_file', 'get_thumbnail', 'has_exif', 'list_all'

    'make', 'model', 'x_resolution', 'y_resolution', 'resolution_unit', 'software', 'artist', 'copyright',
    '_exif_ifd_pointer', '_gps_ifd_pointer', 'compression', 'jpeg_interchange_format', 'jpeg_interchange_format_length',
    'exposure_time', 'f_number', 'exposure_program', 'photographic_sensitivity', 'sensitivity_type',
    'recommended_exposure_index', 'exif_version', 'datetime_original', 'datetime_digitized', 'shutter_speed_value',
    'aperture_value', 'exposure_bias_value', 'metering_mode', 'light_source', 'flash', 'focal_length',
    'subsec_time_original', 'subsec_time_digitized', 'pixel_x_dimension', 'pixel_y_dimension', 'sensing_method',
    'file_source', 'scene_type', 'custom_rendered', 'exposure_mode', 'white_balance', 'focal_length_in_35mm_film',
    'scene_capture_type', 'gain_control', 'contrast', 'saturation', 'sharpness', 'subject_distance_range',
    'body_serial_number', 'lens_specification', 'lens_make', 'lens_model', 'lens_serial_number', 'gps_version_id',
    'gps_latitude_ref', 'gps_latitude', 'gps_longitude_ref', 'gps_longitude', 'gps_altitude_ref', 'gps_altitude',
    'gps_timestamp', 'gps_satellites', 'gps_map_datum', 'gps_datestamp'

    Flash(flash_fired=False, flash_return=FlashReturn.NO_STROBE_RETURN_DETECTION_FUNCTION,
    flash_mode=FlashMode.COMPULSORY_FLASH_FIRING, flash_function_not_present=True, red_eye_reduction_supported=True, reserved=1)
    """
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
    if 'datetime_original' in tags:
        # '2023:04:24 10:13:02
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
        flash = exif['flash'].flash_mode == 1
        if flash:
            data['flash'] = flash

    # TODO LightRoom NO image_width: 256, image_height: 257

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
