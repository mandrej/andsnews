from __future__ import division
import math

LOGARITHMIC, LINEAR = 1, 2


def _calculate_thresholds(min_weight, max_weight, steps):
    delta = (max_weight - min_weight) / steps
    return [min_weight + i * delta for i in range(1, steps + 1)]


def _calculate_tag_weight(weight, max_weight, distribution):
    if distribution == LINEAR or max_weight == 1:
        return weight
    elif distribution == LOGARITHMIC:
        return math.log(weight) * max_weight / math.log(max_weight)
    raise ValueError('Invalid distribution algorithm specified: %s.' % distribution)


def calculate_cloud(tags, steps=8, distribution=LOGARITHMIC):
    """
    tags:  {u'mihailo': 2L, u'urban': 2L, u'belgrade': 3L, u'macro': 5L, ...}
    return [{'count': 2L, 'name': u'mihailo', 'size': 1}, 
            {'count': 5L, 'name': u'macro', 'size': 7}, ...] 
    """
    data = []
    if len(tags) > 0:
        counts = tags.values()
        min_weight = float(min(counts))
        max_weight = float(max(counts)) + 0.0000001
        thresholds = _calculate_thresholds(min_weight, max_weight, steps)
        for key, val in tags.items():
            font_set = False
            tag_weight = _calculate_tag_weight(val, max_weight, distribution)
            for i in range(steps):
                if not font_set and tag_weight <= thresholds[i]:
                    data.append({'name': key, 'count': val, 'size': i + 1})
                    font_set = True
                    break
    return data