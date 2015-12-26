import os
import sys
import json
import logging
import webapp2
from timeit import default_timer
from datetime import datetime, timedelta
from urllib import quote as url_quote
from jinja2.filters import environmentfilter, do_mark_safe, do_truncate
from webapp2_extras.i18n import ngettext, lazy_gettext as _

PY2 = sys.version_info[0] == 2
DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
TIMEOUT = 3600  # 1 hour
PER_PAGE = 12
PHOTOS_PER_PAGE = 24
PHOTOS_MAX_PAGE = 4
ENTRIES_PER_PAGE = 9
ADMIN = 'milan.andrejevic@gmail.com'
MAIL_BODY = """
Dear Administrator:

{error}

{lines}

ANDS Support
"""
FAMILY = [
    ADMIN,
    'mihailo.genije@gmail.com',
    'svetlana.andrejevic@gmail.com',
    'ana.devic@gmail.com',
    'dannytaboo@gmail.com'
]
LANGUAGES = (
    ('en_US', _('english')), ('sr_RS', _('serbian')),
)
COLOR_NAMES = (
    _('red'), _('orange'), _('yellow'), _('green'), _('blue'), _('violet'),
    _('dark'), _('medium'), _('light')
)
# http://www.color-blindness.com/color-name-hue/
# colors from _color.scss
HUE = [
    {'span': range(306, 360) + range(13), 'order': '0', 'name': 'red',    'hex': '#f44336'},
    {'span': range(13, 42),               'order': '1', 'name': 'orange', 'hex': '#ff9800'},
    {'span': range(42, 70),               'order': '2', 'name': 'yellow', 'hex': '#ffeb3b'},
    {'span': range(70, 167),              'order': '3', 'name': 'green',  'hex': '#4caf50'},
    {'span': range(167, 252),             'order': '4', 'name': 'blue',   'hex': '#2196f3'},
    {'span': range(252, 306),             'order': '5', 'name': 'violet', 'hex': '#9c27b0'}
]
LUM = [
    {'span': range(0, 15),                'order': '6', 'name': 'dark',   'hex': '#212121'},
    {'span': range(15, 70),               'order': '7', 'name': 'medium', 'hex': '#616161'},
    {'span': range(70, 101),              'order': '8', 'name': 'light',  'hex': '#bdbdbd'}
]
SAT = [
    {'span': range(0, 6),                               'name': 'monochrome'},
    {'span': range(6, 101),                             'name': 'color'}
]
COLORS = {}
for x in HUE + LUM:
    COLORS[x['name']] = dict((k, v) for k, v in x.items() if k != 'span')

# (math.sqrt(36**2 + 24**2))/25.4 = 1.703410051 (36x24 diagonal in) crop = 1.703410051/0.28 (sensor diagonal)
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
    "Canon EOS 70D": 1.6,
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

ASA = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
       1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400]
LENGTHS = [8, 15, 20, 24, 28, 35, 50, 85, 105, 135, 160, 200, 300, 400, 600]

# LENGTHS = [
#     {'name': _('Extreme Wide'), 'span': range(22)},
#     {'name': _('Wide Angle'), 'span': range(22, 36)},
#     {'name': _('Normal'), 'span': range(36, 71)},
#     {'name': _('Medium Telephoto'), 'span': range(71, 136)},
#     {'name': _('Telephoto'), 'span': range(136, 301)},
# ]

if not PY2:
    unichr = chr
    range_type = range
    text_type = str
    string_types = (str,)
    integer_types = (int,)

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())
else:
    unichr = unichr
    text_type = unicode
    range_type = xrange
    string_types = (str, unicode)
    integer_types = (int, long)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()


def timeit(f):
    def wrapper(*args, **kw):
        timer = default_timer
        start = timer()
        result = f(*args, **kw)
        end = timer()
        logging.debug('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, end - start))
        return result

    return wrapper


def version():
    return os.environ.get('CURRENT_VERSION_ID').split('.').pop(0)


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


def image_dimension(obj):
    return '{0} x {1}'.format(*obj.dim)


def boolimage(value):
    """ {{ object.key.name|incache|boolimage }} """
    if value is True:
        return do_mark_safe('<i class="fa fa-check-circle" style="color: #060"></i>')
    else:
        return do_mark_safe('<i class="fa fa-minus-circle" style="color: #c00"></i>')


@environmentfilter
def css_classes(env, classes):
    return ' '.join(x for x in classes if x) or env.undefined(hint='No classes requested')


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


def truncate(string, length=255, killwords=False):
    return do_truncate(string, length, killwords)


def unicode_urlencode(obj, charset='utf-8', for_qs=False):
    """URL escapes a single bytestring or unicode string with the
    given charset if applicable to URL safe quoting under all rules
    that need to be considered under all supported Python versions.

    If non strings are provided they are converted to their unicode
    representation first.
    """
    if not isinstance(obj, string_types):
        obj = text_type(obj)
    if isinstance(obj, text_type):
        obj = obj.encode(charset)
    safe = for_qs and b'' or b'/'
    rv = text_type(url_quote(obj, safe))
    if for_qs:
        rv = rv.replace('%20', '+')
    return rv


def do_urlencode(value):
    """Escape strings for use in URLs (uses UTF-8 encoding).  It accepts both
    dictionaries and regular strings as well as pairwise iterables.

    .. versionadded:: 2.7
    """
    itemiter = None
    if isinstance(value, dict):
        itemiter = iteritems(value)
    elif not isinstance(value, string_types):
        try:
            itemiter = iter(value)
        except TypeError:
            pass
    if itemiter is None:
        return unicode_urlencode(value)
    return u'&'.join(unicode_urlencode(k) + '=' +
                     unicode_urlencode(v, for_qs=True)
                     for k, v in itemiter)


CONFIG = {
    'webapp2_extras.jinja2': {
        'globals': {
            'year': year,
            'version': version,
            'language': language,
            'all_languages': LANGUAGES,
            'devel': DEVEL,
            'uri_for': webapp2.uri_for,
        },
        'filters': {
            'boolimage': boolimage,
            'to_date': to_date,
            'to_datetime': to_datetime,
            'image_url_by_num': image_url_by_num,
            'image_dimension': image_dimension,
            'css_classes': css_classes,
            'filesizeformat': filesizeformat,
            'timesince': timesince_jinja,
            'to_json': to_json,
            'split': split,
            'urlencode': do_urlencode,
            'truncate': truncate,
        },
        'environment_args': {
            'autoescape': True,
            'trim_blocks': True,
            'extensions': ['jinja2.ext.autoescape', 'jinja2.ext.with_', 'jinja2.ext.do', 'jinja2.ext.i18n']
        },
    },
    'webapp2_extras.i18n': {
        'translations_path': 'locale',
        'default_locale': 'en_US'
    },
    'webapp2_extras.sessions': {'secret_key': 'kTlR8YMGAMkL7L9JilpgADfh8MRFz2fkeBJ6+VM9FD4=', 'session_max_age': 86400}
}
# < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;
