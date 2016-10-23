import os
from google.appengine.api import app_identity

BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')

COLOR_NAMES = (
    'red', 'orange', 'yellow', 'green', 'blue', 'violet', 'dark', 'medium', 'light'
)
# http://www.color-blindness.com/color-name-hue/
HUE = [
    {'span': range(306, 360) + range(13), 'order': '0', 'name': 'red',    'hex': '#c00'},
    {'span': range(13, 42),               'order': '1', 'name': 'orange', 'hex': '#f90'},
    {'span': range(42, 70),               'order': '2', 'name': 'yellow', 'hex': '#ff0'},
    {'span': range(70, 167),              'order': '3', 'name': 'green',  'hex': '#0c0'},
    {'span': range(167, 252),             'order': '4', 'name': 'blue',   'hex': '#06f'},
    {'span': range(252, 306),             'order': '5', 'name': 'violet', 'hex': '#c0c'}
]
LUM = [
    {'span': range(0, 15),                'order': '6', 'name': 'dark',   'hex': '#111'},
    {'span': range(15, 70),               'order': '7', 'name': 'medium', 'hex': '#555'},
    {'span': range(70, 101),              'order': '8', 'name': 'light',  'hex': '#ccc'}
]
SAT = [
    {'span': range(0, 6),                               'name': 'monochrome'},
    {'span': range(6, 101),                             'name': 'color'}
]
COLORS = HUE + LUM

ASA = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
       1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400]

# < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;
