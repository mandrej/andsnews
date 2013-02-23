import os
from webapp2_extras.i18n import lazy_gettext as _

DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
RFC822 = '%a, %d %b %Y %I:%M:%S %p GMT'
TIMEOUT = 3600  # 1 hour
PER_PAGE = 12
RESULTS = 12
LIMIT = 1024*1024
ADMIN_JID = 'milan.andrejevic@gmail.com'
FAMILY = ['mihailo.genije@gmail.com', 'milan.andrejevic@gmail.com',
          'svetlana.andrejevic@gmail.com', 'ana.devic@gmail.com', 'dannytaboo@gmail.com']

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

LANGUAGES = (
    ('en_US', _('english')), ('sr_RS', _('serbian')),
)
WEEKDAYS = {
    0: _('Monday'), 1: _('Tuesday'), 2: _('Wednesday'), 3: _('Thursday'),
    4: _('Friday'), 5: _('Saturday'), 6: _('Sunday')
}
MONTHS = {
    1: _('January'), 2: _('February'), 3: _('March'), 4: _('April'), 5: _('May'), 6: _('June'),
    7: _('July'), 8: _('August'), 9: _('September'), 10: _('October'), 11: _('November'), 12: _('December')
}
MONTHS_3 = {
    1: _('jan'), 2: _('feb'), 3: _('mar'), 4: _('apr'), 5: _('may'), 6: _('jun'),
    7: _('jul'), 8: _('aug'), 9: _('sep'), 10: _('oct'), 11: _('nov'), 12: _('dec')
}
MONTHS_AP = {
    1: _('Jan.'), 2: _('Feb.'), 3: _('March'), 4: _('April'), 5: _('May'), 6: _('June'),
    7: _('July'), 8: _('Aug.'), 9: _('Sept.'), 10: _('Oct.'), 11: _('Nov.'), 12: _('Dec.')
}
COLORNAMES = (
    _('red'), _('orange'), _('yellow'), _('green'), _('teal'), _('blue'),
    _('purple'), _('pink'), _('dark'), _('medium'), _('light'),
)

HUE = [
    {'span': map(lambda x: x+360 if x < 0 else x, xrange(-10, 10)), 'order': '0', 'name': 'red', 'hex': '#cc0000'},  # 0
    {'span': xrange(10, 40), 'order': '1', 'name': 'orange', 'hex': '#ff7f00'},  # 30
    {'span': xrange(40, 60), 'order': '2', 'name': 'yellow', 'hex': '#ffff0f'},  # 60
    {'span': xrange(60, 150), 'order': '3', 'name': 'green', 'hex': '#00bf00'},  # 120
    {'span': xrange(150, 190), 'order': '4', 'name': 'teal', 'hex': '#00bfbf'},  # 180
    {'span': xrange(190, 240), 'order': '5', 'name': 'blue', 'hex': '#005fbf'},  # 210
    {'span': xrange(240, 290), 'order': '6', 'name': 'purple', 'hex': '#5f00bf'},  # 270
    {'span': xrange(290, 350), 'order': '7', 'name': 'pink', 'hex': '#bf005f'}  # 330
]
LUM = [
    {'span': xrange(0, 10), 'order': '8', 'name': 'dark', 'hex': '#191919'},
    {'span': xrange(10, 40), 'order': '9', 'name': 'medium', 'hex': '#4c4c4c'},
    {'span': xrange(40, 101), 'order': 'a', 'name': 'light', 'hex': '#cccccc'}
]
SAT = [
    {'span': xrange(0, 10), 'name': 'monochrome'},
    {'span': xrange(10, 101), 'name': 'color'}
]

COLORS = {}
for x in HUE:
    COLORS['hue-%s' % x['name']] = {'hex': x['hex'], 'field': 'hue', 'name': x['name'], 'order': x['order']}

for x in LUM:
    COLORS['lum-%s' % x['name']] = {'hex': x['hex'], 'field': 'lum', 'name': x['name'], 'order': x['order']}

"""
import datetime, time, random
print time.strftime('%y%W', datetime.datetime.now().timetuple())

sid = '~`!@#$%^&*()_-+=|\{[}]abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
print ''.join(random.sample(sid, 50))

find . -type f -name "*.pyc" -exec rm -f {} \;
"""