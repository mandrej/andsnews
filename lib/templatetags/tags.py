from __future__ import division
import os
import datetime
from google.appengine.api import memcache
from django import template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django import get_version
from django.conf import settings
register = template.Library()

@register.simple_tag
def version():
    return os.environ.get('CURRENT_VERSION_ID').split('.').pop(0)

@register.simple_tag
def gaesdk_version():
    return os.environ.get('SERVER_SOFTWARE')

@register.simple_tag
def django_version():
    return get_version()

@register.filter
def subpage(value, arg):
    return (int(value)-1)*settings.PER_PAGE+int(arg)

@register.filter
def incache(key, size=None):
    """
    {{ object.key.name|yesno:"yes,no" }}
    """
    if memcache.get(key): return True
    else: return False

@register.filter
def boolimage(value):
    """ {{ object.key.name|incache:"small"|yesno:"yes,no"|boolimage }} """
    return mark_safe('<img src="/static/images/icon_%s.png" alt="%s"/>' % (value, value))

@register.filter
def image_url_by_num(obj, arg):
    """ {{ object|image_url_by_num:form.initial.ORDER }}/small
        {{ object|image_url_by_num:object.front }}/small """
    return obj.image_url(arg)

@register.filter
def snippet(html, phrase):
    """ {{ object.body|snippet:phrase """
    pad = 10
    text = strip_tags(html)
    words_original = [x for x in text.split() if x != '']
    words_lowercase = enumerate([x.lower() for x in words_original])
    
    indexes = []
    for term in phrase.lower().split():
        indexes += [i for i, x in words_lowercase if x == term]
    if not indexes:
        return ' '.join(words_original[:pad*2])
    
    part = '<p>'
    for idx in sorted(indexes)[:3]:
        part += ' '.join(words_original[idx-pad: idx+pad]) + '<br/>'
    part += '</p>'
    return mark_safe(part)

#------------------ Template Helpers -------------------------------------------

#            message_key     h4 title                      css_class
MESSAGES = {'servererror':  [_('500 Server error'),       'error'  ],
            'unavailable':  [_('503 Service unavailable'),'error'  ],
            'notfound':     [_('404 Page not found'),     'error'  ],
            'forbidden':    [_('403 Access denied'),      'error'  ],
            'noresults':    [_('No results'),             'info'   ],
            'error':        [_('Error occurred'),         'error'  ]}

class PopupNode(template.Node):
    def __init__(self, message_key, nodelist):
        self.message_key = message_key
        self.nodelist = nodelist
    def render(self, context):
        tmpl = template.loader.get_template('snippets/msg.html')
        context['id'] = self.message_key
        context['title'] = MESSAGES[self.message_key][0]
        context['css_class'] = MESSAGES[self.message_key][1]
        body = self.nodelist.render(context).strip()
        context['body'] = mark_safe(body)
        return tmpl.render(context)

@register.tag
def popup(parser, token):
    """
    {% popup noresults %}
        <p>{% trans "No polls available." %}</p>
    {% endpopup %}
    """
    bits = token.contents.split()
    message_key = bits[1]
    nodelist = parser.parse(('endpopup',))
    parser.delete_first_token()
    return PopupNode(message_key, nodelist)

FORM_ROW = """
<label for="id_{{ F.html_name }}"{% if F.field.required %} class="required"{% endif %}>{{ F.label }}</label>
{{ F }}<span class="error C_{{ F.html_name }}"><!-- -->{{ F.errors|join:", " }}</span>
"""

@register.filter
def form_row(value, arg=None):
    """ {{ form.is_active|form_row:"class" }} """
    if arg:
        row = template.Template("""<p class="%s">%s</p>""" % (arg, FORM_ROW))
    else:
        row = template.Template("""<p>%s</p>""" % FORM_ROW)
    return row.render(template.Context({'F': value}))

@register.inclusion_tag('snippets/stats.html', takes_context=True)
def stats(context):
    stats = memcache.get_stats()
    if stats:
        hits = stats.get('hits', 0)
        misses = stats.get('misses', 0)
        all = hits + misses
        if all > 0:
            hit_ratio = 100*hits/all
            delta_t = datetime.timedelta(seconds=stats['oldest_item_age'])
            oldest = datetime.datetime.now() - delta_t
            return {'stats': stats,
                    'hit_ratio': hit_ratio,
                    'oldest': oldest}

@register.inclusion_tag('snippets/paginator.html', takes_context=True)
def paginator(context):
    return context
