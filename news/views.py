import webapp2
import re, datetime, time
from google.appengine.api import users, urlfetch, memcache
from google.appengine.ext import ndb
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form, widgets, fields, validators
from models import Feed
from lib import feedparser
from common import  BaseHandler, Paginator, Filter, TagsField
from settings import TIMEOUT

PER_PAGE = 12
FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
ADS = (
    re.compile(r'<div class="(feedflare|blogger-post-footer)">.+?</div>', re.DOTALL),
    re.compile(r'<p><a.+(ads|auslieferung|feedads|pheedcontent).*?>.+?</a></p>', re.DOTALL),
    re.compile(r'<img\b[^<]*(ads|blogger|imp|creatives|feeds|pixel|segment|blogsmithmedia).*?>'),
    re.compile(r'background-color:\s?.+?;?')
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

class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Feed._properties[k] == v for k, v in f.parameters.items()]
        query = Feed.query(*filters).order(-Feed.date)

        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query, per_page=PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'kind': 'Feed',
                'objects': objects,
                'filter': f.parameters,
                'filter_url': f.url,
                'filter_title': f.title,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('news/index.html', data)

class Detail(BaseHandler):
    def get(self, slug):
        error = ''
        obj = Feed.get_by_id(slug)
        if obj is None:
            webapp2.abort(404)
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
                        memcache.add(slug, news, TIMEOUT)
                        obj.put_async()
                    else:
                        error = _('Feed server send no entries')
                else:
                    error = _('Feed server returns %s code' % status)

        self.render_template('news/detail.html', {'object': obj, 'news': news, 'error': error, 'filter': None})

class AddForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    slug = fields.TextField(_('Slug'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    url = fields.TextField(_('Url'), validators=[validators.DataRequired(), validators.URL()])

    def validate_slug(self, field):
        if Feed.get_by_id(field.data):
            raise validators.ValidationError(_('Record with this slug already exist'))

class EditForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    url = fields.TextField(_('Url'), validators=[validators.DataRequired(), validators.URL()])
    date = fields.DateTimeField(_('Taken'))

class Add(BaseHandler):
    #@admin_required
    def get(self, form=None):
        if form is None:
            form = AddForm()
        self.render_template('news/form.html', {'form': form, 'filter': None})

    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Feed(id=form.slug.data)
            obj.add(form.data)
            self.redirect('/news')
        else:
            self.render_template('news/form.html', {'form': form, 'filter': None})

class Edit(BaseHandler):
    #@admin_required
    def get(self, slug, form=None):
        obj = Feed.get_by_id(slug)
        if form is None:
            form = EditForm(obj=obj)
        self.render_template('news/form.html', {'form': form, 'object': obj, 'filter': None})

    def post(self, slug):
        obj = Feed.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect('/news')
        else:
            self.render_template('news/form.html', {'form': form, 'object': obj, 'filter': None})