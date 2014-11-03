__author__ = 'milan'

import os
import json
import webapp2
from datetime import datetime, timedelta
from google.appengine.api import memcache
from jinja2.filters import environmentfilter, do_mark_safe
from webapp2_extras.i18n import ngettext, lazy_gettext as _

DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
TIMEOUT = 3600  # 1 hour
PER_PAGE = 12
PHOTOS_PER_PAGE = 24
PHOTOS_LATEST = 5
ENTRIES_PER_PAGE = 9
RFC822 = '%a, %d %b %Y %I:%M:%S %p GMT'
ADMIN_JID = 'milan.andrejevic@gmail.com'
FAMILY = ['mihailo.genije@gmail.com', 'milan.andrejevic@gmail.com',
          'svetlana.andrejevic@gmail.com', 'ana.devic@gmail.com', 'dannytaboo@gmail.com']
LANGUAGES = (
    ('en_US', _('english')), ('sr_RS', _('serbian')),
)
COLOR_NAMES = (
    _('red'), _('orange'), _('yellow'), _('green'), _('teal'), _('blue'),
    _('purple'), _('pink'), _('dark'), _('medium'), _('light')
)
HUE = [
    {'span': range(342, 360) + range(12), 'order': '0', 'name': 'red', 'hex': '#cc0000'},  # 0
    {'span': range(12, 40), 'order': '1', 'name': 'orange', 'hex': '#ff7f00'},  # 30
    {'span': range(40, 69), 'order': '2', 'name': 'yellow', 'hex': '#ffff0f'},  # 60
    {'span': range(69, 143), 'order': '3', 'name': 'green', 'hex': '#00bf00'},  # 120
    {'span': range(143, 192), 'order': '4', 'name': 'teal', 'hex': '#00bfbf'},  # 180
    {'span': range(192, 244), 'order': '5', 'name': 'blue', 'hex': '#005fbf'},  # 210
    {'span': range(244, 287), 'order': '6', 'name': 'purple', 'hex': '#5f00bf'},  # 270
    {'span': range(287, 342), 'order': '7', 'name': 'pink', 'hex': '#bf005f'}  # 330
]
LUM = [
    {'span': range(0, 10), 'order': '8', 'name': 'dark', 'hex': '#191919'},
    {'span': range(10, 75), 'order': '9', 'name': 'medium', 'hex': '#4c4c4c'},
    {'span': range(75, 101), 'order': 'a', 'name': 'light', 'hex': '#cccccc'}
]
SAT = [
    {'span': range(0, 20), 'name': 'monochrome'},
    {'span': range(20, 101), 'name': 'color'}
]
COLORS = {}
for x in HUE + LUM:
    COLORS[x['name']] = dict((k, v) for k, v in x.items() if k != 'span')

# math.sqrt(36**2 + 24**2) = 43.266615305567875 crop = 43.266615305567875/(0.28*25.4)
CROPS = {
    "Contax 137 MD Quartz": 1.0,
    "Canon EOS 5D Mark III": 1.0,
    "NIKON D700": 1.0,
    "NIKON D300": 1.5,
    "NIKON D200": 1.5,
    "NIKON D80": 1.5,
    "NIKON D70": 1.5,
    "FUJIFILM X-E1": 1.5,
    "SIGMA dp2 Quattro": 1.5,
    "Canon EOS 20D": 1.6,
    "Canon EOS 40D": 1.6,
    "Canon EOS 400D DIGITAL": 1.6,
    "OLYMPUS IMAGING CORP. E-P1": 2.0,
    "Canon PowerShot A80": 4.6,
    "Canon IXUS 115 HS": 5.6,
    "PENTACON Luxmedia 8403": 6.0,
    "SONY DSC-T7": 6.0,
    "SONY DSC-W110": 6.0,
    "SAMSUNG SM-T520": 6.1,
    "OLYMPUS IMAGING CORP. IR-500": 6.6,
    "SAMSUNG GT-C3530": 7.0,
    "LGE Nexus 4": 7.6,
    "LGE Nexus 5": 7.6,
    "google Nexus S": 8.8
}

ASA = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 3500, 3200, 6400]
LENGTHS = [8, 15, 20, 24, 28, 35, 50, 85, 105, 135, 200, 300, 400, 600]


def version():
    return os.environ.get('CURRENT_VERSION_ID').split('.').pop(0)


def gaesdk():
    return os.environ.get('SERVER_SOFTWARE')


def language(code):
    return code.split('_')[0]


def year():
    date = datetime.now()
    return date.strftime('%Y')


def to_date(value, format='%Y-%m-%d'):
    return value.strftime(format)


def to_datetime(value, format='%Y-%m-%dT%H:%M:%S'):
    return value.strftime(format)


def image_url_by_num(obj, arg):
    """ {{ object|image_url_by_num:form.initial.ORDER }}/small
        {{ object|image_url_by_num:object.front }}/small """
    return obj.image_url(arg)


def incache(key):
    if memcache.get(key):
        return True
    else:
        return False


def boolimage(value):
    """ {{ object.key.name|incache|boolimage }} """
    if value is True:
        return do_mark_safe('<i class="fa fa-check-circle" style="color: #060"></i>')
    else:
        return do_mark_safe('<i class="fa fa-minus-circle" style="color: #c00"></i>')


@environmentfilter
def css_classes(env, classes):
    return u' '.join(unicode(x) for x in classes if x) or env.undefined(hint='No classes requested')


def filesizeformat(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and "KiB" or "kB"),
        (binary and "MiB" or "MB"),
        (binary and "GiB" or "GB"),
        (binary and "TiB" or "TB"),
        (binary and "PiB" or "PB"),
        (binary and "EiB" or "EB"),
        (binary and "ZiB" or "ZB"),
        (binary and "YiB" or "YB")
    ]
    if bytes == 1:
        return "1 Byte"
    elif bytes < base:
        return "%d Bytes" % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if bytes < unit:
                return '%.1f %s' % ((base * bytes / unit), prefix)
        return '%.1f %s' % ((base * bytes / unit), prefix)


def timesince_jinja(d, now=None):
    # http://stackoverflow.com/questions/8292477/localized-timesince-filter-for-jinja2-with-gae
    chunks = (
        (60 * 60 * 24 * 365, lambda n: ngettext('year', 'years', n)),
        (60 * 60 * 24 * 30, lambda n: ngettext('month', 'months', n)),
        (60 * 60 * 24 * 7, lambda n: ngettext('week', 'weeks', n)),
        (60 * 60 * 24, lambda n: ngettext('day', 'days', n)),
        (60 * 60, lambda n: ngettext('hour', 'hours', n)),
        (60, lambda n: ngettext('minute', 'minutes', n))
    )
    if not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime):
        now = datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.now()

    delta = now - (d - timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        return u'0 ' + _('minutes')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    s = _('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    if i + 1 < len(chunks):
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += _(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
    return s


def to_json(value):
    # http://stackoverflow.com/questions/8727349/converting-dict-object-to-string-in-django-jinja2-template
    return do_mark_safe(json.dumps(value))


def split(value, sep=','):
    if value:
        return value.split(sep)
    return []


CONFIG = {
    'webapp2_extras.jinja2': {
        'globals': {
            'year': year,
            'version': version,
            'gaesdk': gaesdk,
            'language': language,
            'all_languages': LANGUAGES,
            'devel': DEVEL,
            'uri_for': webapp2.uri_for,
            'prev_class': 'prev fa fa-chevron-left fa-4x',
            'next_class': 'next fa fa-chevron-right fa-4x',
        },
        'filters': {
            'incache': incache,
            'boolimage': boolimage,
            'to_date': to_date,
            'to_datetime': to_datetime,
            'image_url_by_num': image_url_by_num,
            'css_classes': css_classes,
            'filesizeformat': filesizeformat,
            'timesince': timesince_jinja,
            'to_json': to_json,
            'split': split,
        },
        'environment_args': {
            'autoescape': False,
            'trim_blocks': True,
            'extensions': ['jinja2.ext.autoescape', 'jinja2.ext.with_', 'jinja2.ext.i18n', 'jinja2spaceless.Spaceless']
        },
    },
    'webapp2_extras.i18n': {
        'translations_path': 'locale',
        'default_locale': 'en_US'
    },
    'webapp2_extras.sessions': {'secret_key': 'kTlR8YMGAMkL7L9JilpgADfh8MRFz2fkeBJ6+VM9FD4=', 'session_max_age': 86400}
}
# < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;