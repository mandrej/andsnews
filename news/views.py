import re, datetime, time
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import ndb
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django import forms
from models import Feed
from lib import feedparser
from lib.comm import Paginator, Filter, login_required, admin_required
from django.conf import settings

PER_PAGE = 12
FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
ADS = (
    re.compile(r'<div class="(feedflare|blogger-post-footer)">.+?</div>', re.DOTALL),
    re.compile(r'<p><a.+(ads|auslieferung|feedads|pheedcontent).*?>.+?</a></p>', re.DOTALL),
    re.compile(r'<img\b[^<]*(ads|blogger|imp|creatives|feeds|pixel|segment|blogsmithmedia).*?>'),
)

def make_date(tt):
    """ Convert tt to datetime.datetime
        (2009, 7, 29, 14, 39, 12, 2, 210, 0) """
    try:
        return datetime.datetime.fromtimestamp(time.mktime(tt))
    except TypeError:
        return None

def parse_date(str):
    """ Convert date from string FORMAT to tt
        'Wed, 29 Jul 2009 21:41:18 GMT' """
    try:
        tt = time.strptime(str, FORMAT)
    except ValueError:
        return None
    else:
        return make_date(tt)

def rewrite(news):
    stripADS = True
    for entry in news.entries:
        if hasattr(entry, 'summary'):
            entry.content = entry.summary
        elif hasattr(entry, 'content'):
            entry.content = entry.content[0].value
        if hasattr(entry, 'updated_parsed'):
            entry.date = make_date(entry.updated_parsed)
        elif hasattr(entry, 'published_parsed'):
            entry.date = make_date(entry.published_parsed)

        if stripADS:
            original = entry.content
            for ad in ADS:
                entry.content = re.sub(ad, '', entry.content)
            if entry.content == original:
                stripADS = False
    return news

def update(result):
    news = None
    date = datetime.datetime.now()
    feed = feedparser.parse(result.content)
    if feed.bozo == 0:
        news = rewrite(feed)
        if news.entries:
            if 'updated_parsed' in news.feed:
                date = make_date(news.feed['updated_parsed'])
            elif 'date' in result.headers:
                date = parse_date(result.headers['date'])
    return news, date

def index(request, field=None, value=None, tmpl='news/index.html'):
    f = Filter(field, value)
    filters = [Feed._properties[k] == v for k, v in f.parameters.items()]
    query = Feed.query(*filters).order(-Feed.date)

    page = int(request.GET.get('page', 1))
    paginator = Paginator(query, per_page=PER_PAGE)
    objects, has_next = paginator.page(page)
    
    data = {'objects': objects,
            'filter': f.parameters,
            'filter_url': f.url,
            'filter_title': f.title,
            'page': page,
            'has_next': has_next,
            'has_previous': page > 1}
    return render(request, tmpl, data)

def detail(request, slug, tmpl='news/detail.html'):
    error = ''
    obj = Feed.get_by_id(slug)
    if obj is None:
        raise Http404
    news = memcache.get(slug)
    if not news:
        rpc = urlfetch.create_rpc(deadline=20)
        urlfetch.make_fetch_call(rpc, obj.url)
        try:
            result = rpc.get_result()
        except urlfetch.DownloadError:
            error = _('Feed server timeout')
        else:
            status = result.status_code
            if status == 200:
                news, obj.date = update(result)
                if news.entries:
                    memcache.add(slug, news, settings.TIMEOUT)
                    obj.put_async()
                else:
                    error = _('Feed server send no entries')
            else:
                error = _('Feed server returns %s code' % status)
    
    return render(request, tmpl, {'object': obj, 'news': news, 'error': error})

class AddForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                    error_messages={'required': _('Required field')})
    slug = forms.SlugField(label=_('Slug'), error_messages={'required': _('Required field')})
    tags = forms.CharField(label=_('Tags'), required=False)
    url = forms.URLField(label=_('Url'), error_messages={'required': _('Required field')})

    def clean_slug(self):
        data = self.cleaned_data['slug']
        if Feed.get_by_id(data):
            raise forms.ValidationError(_('Record with this slug already exist'))
        return data

class EditForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                error_messages={'required': _('Required field')})
    slug = forms.SlugField(label=_('Slug'), required=False,
                widget=forms.TextInput(attrs={'disabled': 'disabled', 'class': 'disabled'}))
    tags = forms.CharField(label=_('Tags'), required=False)
    url = forms.URLField(label=_('Url'), error_messages={'required': _('Required field')})
    date = forms.DateTimeField(label=_('Date'), required=False,
                widget=forms.TextInput(attrs={'disabled': 'disabled', 'class': 'disabled'}))

@login_required
def add(request, tmpl='news/form.html'):
    data = {}
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            obj = Feed(id=data['slug'],
                       headline=data['headline'],
                       url = data['url'])
            obj.add(data)
            return redirect('/news')
    else:
        form = AddForm()

    data['form'] = form
    return render(request, tmpl, data)

@admin_required
def edit(request, slug, tmpl='news/form.html'):
    obj = Feed.get_by_id(slug)
    data = {'object': obj}
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            data.update(form.cleaned_data)
            obj.edit(data)
            return redirect(obj.get_absolute_url())
    else:
        form = EditForm(initial={'headline': obj.headline,
                                 'slug': obj.key.string_id(),
                                 'tags': ', '.join(obj.tags),
                                 'url': obj.url,
                                 'date': obj.date})

    data['form'] = form
    return render(request, tmpl, data)

@admin_required
def delete(request, slug, tmpl='snippets/confirm.html'):
    obj = Feed.get_by_id(slug)
    if request.method == 'POST':
        obj.delete()
        return redirect('/news')
    elif request.is_ajax():
        data = {'object': obj, 'post_url': request.path}
        return render(request, tmpl, data)
