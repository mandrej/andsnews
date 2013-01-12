import os

DEBUG = True
DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
LANGUAGE_COOKIE_NAME = 'ands_lang'
TIMEOUT = 3600 # 1 hour
PER_PAGE = 12
LIMIT = 1024*1024
ADMIN_JID = 'milan.andrejevic@gmail.com'
FAMILY = ['mihailo.genije@gmail.com', 'milan.andrejevic@gmail.com',
          'svetlana.andrejevic@gmail.com', 'ana.devic@gmail.com', 'dannytaboo@gmail.com']

HUE = [
    {'span': map(lambda x: x+360 if x<0 else x, xrange(-10, 10)), 'order': '0', 'name': 'red', 'hex': '#cc0000'}, # 0
    {'span': xrange(10, 40), 'order': '1', 'name': 'orange', 'hex': '#ff7f00'}, # 30
    {'span': xrange(40, 60), 'order': '2', 'name': 'yellow', 'hex': '#ffff0f'}, # 60
    {'span': xrange(60, 150), 'order': '3', 'name': 'green', 'hex': '#00bf00'}, # 120
    {'span': xrange(150, 190), 'order': '4', 'name': 'teal', 'hex': '#00bfbf'}, # 180
    {'span': xrange(190, 240), 'order': '5', 'name': 'blue', 'hex': '#005fbf'}, # 210
    {'span': xrange(240, 290), 'order': '6', 'name': 'purple', 'hex': '#5f00bf'}, # 270
    {'span': xrange(290, 350), 'order': '7', 'name': 'pink', 'hex': '#bf005f'} # 330
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