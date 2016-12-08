import unittest

FB = {
    "2016": {
        "count" : 10,
        "field_name" : "date",
        "order" : -16,
        "value" : 2016
    },
    "b&w": {
        "count" : 10,
        "field_name" : "tags",
        "order" : "20b&w",
        "value" : "b&w"
    },
    "still life": {
        "count" : 10,
        "field_name" : "tags",
        "order" : "20still life",
        "value" : "still life"
    },
    "street": {
        "count" : 10,
        "field_name" : "tags",
        "order" : "20street",
        "value" : "street"
    },
    "new": {
        "count": 0,
        "field_name": "tags",
        "order": "20new",
        "value": "new"
    },
    "SIGMA dp2 Quattro": {
        "count" : 10,
        "field_name" : "model",
        "order" : "30SIGMA dp2 Quattro",
        "value" : "SIGMA dp2 Quattro"
    }
}

DEVEL = True


def update_filters(new_pairs, old_pairs):
    payload = {}

    if new_pairs and old_pairs:  # EDIT
        pairs = set(new_pairs) ^ set(old_pairs)
    elif new_pairs:  # ADD
        pairs = set(new_pairs)
    elif old_pairs:  # DEL
        pairs = set(old_pairs)

    for field, value in pairs:
        key = str(value)
        count = 0

        obj = FB.get(key)  # <type 'dict'>
        if obj and obj['count']:
            count = obj['count']

        if (field, value) in old_pairs:
            FB.get(key)['count'] = count - 1
            print 'decrease {} {}'.format(value, count)
        if (field, value) in new_pairs:
            FB.get(key)['count'] = count + 1
            print 'increse {} {}'.format(value, count)

    for field, value in set(new_pairs) ^ set(old_pairs):
        print 'latest {} {}'.format(field, value)

    return payload


class UpdateTest(unittest.TestCase):
    def test_add(self):
        new_pairs = [('date', 2016), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        old_pairs = []
        update_filters(new_pairs, old_pairs)
        print '-----------------------'
        for k, v in FB.items():
            print '{} {}'.format(k, v['count'])

    def test_edit(self):
        new_pairs = [('date', 2016), ('tags', 'street'), ('model', 'SIGMA dp2 Quattro')]
        old_pairs = [('date', 2016), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        update_filters(new_pairs, old_pairs)
        print '-----------------------'
        for k, v in FB.items():
            print '{} {}'.format(k, v['count'])

    def test_del(self):
        new_pairs = []
        old_pairs = [('date', 2016), ('tags', 'street'), ('model', 'SIGMA dp2 Quattro')]
        update_filters(new_pairs, old_pairs)
        print '-----------------------'
        for k, v in FB.items():
            print '{} {}'.format(k, v['count'])
