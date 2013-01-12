ugettext = lambda s: s
ungettext = lambda s: s

WEEKDAYS = {
    0:ugettext('Monday'), 1:ugettext('Tuesday'),  2:ugettext('Wednesday'), 3:ugettext('Thursday'),
    4:ugettext('Friday'), 5:ugettext('Saturday'), 6:ugettext('Sunday')
}
MONTHS = {
    1:ugettext('January'),  2:ugettext('February'),  3:ugettext('March'),
    4:ugettext('April'),    5:ugettext('May'),       6:ugettext('June'),
    7:ugettext('July'),     8:ugettext('August'),    9:ugettext('September'),
    10:ugettext('October'), 11:ugettext('November'), 12:ugettext('December')
}
MONTHS_3 = {
    1:ugettext('jan'),  2:ugettext('feb'),  3:ugettext('mar'),
    4:ugettext('apr'),  5:ugettext('may'),  6:ugettext('jun'),
    7:ugettext('jul'),  8:ugettext('aug'),  9:ugettext('sep'),
    10:ugettext('oct'), 11:ugettext('nov'), 12:ugettext('dec')
}
MONTHS_AP = {
    1:ugettext('Jan.'), 2:ugettext('Feb.'), 3:ugettext('March'), 4:ugettext('April'), 5:ugettext('May'),   6:ugettext('June'),
    7:ugettext('July'), 8:ugettext('Aug.'), 9:ugettext('Sept.'), 10:ugettext('Oct.'), 11:ugettext('Nov.'), 12:ugettext('Dec.')
}
# django.utils.timesince
CHUNKS = (
    (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
    (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
    (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
    (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
    (60 * 60, lambda n: ungettext('hour', 'hours', n)),
    (60, lambda n: ungettext('minute', 'minutes', n))
)
TIMESINCE = (
    ugettext("%(number)d %(type)s"),
    ugettext(", %(number)d %(type)s"),
)
COLORNAMES = (
    ugettext('red'), ugettext('orange'), ugettext('yellow'), ugettext('green'), ugettext('teal'), ugettext('blue'), ugettext('purple'), ugettext('pink'),
    ugettext('dark'), ugettext('medium'), ugettext('light'),
)
