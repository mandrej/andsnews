import re
import datetime
import time
import rfc822
from StringIO import StringIO

from google.appengine.ext import ndb
from google.appengine.api import memcache
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required

from wtforms import Form, fields, validators
from models import Feed
from lib import feedparser
from handlers import BaseHandler, csrf_protected, Paginator, Filter, TagsField
from config import TIMEOUT

FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
ADS = (
    re.compile(r'<div class="(feedflare|mf-viral|blogger-post-footer)">.+?</div>', re.DOTALL),
    #re.compile(r'<p><a.+(ads|auslieferung|feedads|pheedcontent).*?>.+?</a></p>', re.DOTALL),
    #re.compile(r'<img\b[^<]*(ads|blogger|imp|creatives|feeds|pixel|segment|blogsmithmedia).*?>'),
    #re.compile(r'background-color:\s?.+?;?')
)


def make_date(tt):
    """ Convert time tuple to datetime.datetime
        (2009, 7, 29, 14, 39, 12, 2, 210, 0) """
    return datetime.datetime.fromtimestamp(time.mktime(tt))


def parse_date(str):
    """ Convert date from string FORMAT to time tuple
        'Wed, 29 Jul 2009 21:41:18 GMT' """
    tt = rfc822.parsedate(str)
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


@ndb.tasklet
def get_feed_async(url):
    ctx = ndb.get_context()
    result = yield ctx.urlfetch(url)
    if result.status_code == 200:
        raise ndb.Return(result)


class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Feed._properties[k] == v for k, v in f.parameters.items()]
        query = Feed.query(*filters).order(-Feed.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('news/index.html', data)


class Detail(BaseHandler):
    @ndb.toplevel
    def get(self, slug):
        error = ''
        obj = Feed.get_by_id(slug)
        if obj is None:
            self.abort(404)
        news = memcache.get(slug)
        if not news:
            future = get_feed_async(obj.url)
            if future.state:  # 1
                result = future.get_result()
                feed = feedparser.parse(StringIO(result.content))

                if feed.bozo == 0:
                    news = rewrite(feed)
                    if news.entries:
                        date = datetime.datetime.now()
                        if 'updated_parsed' in news.feed:
                            date = make_date(news.feed['updated_parsed'])
                        elif 'date' in result.headers:
                            date = parse_date(result.headers['date'])

                        memcache.add(slug, news, TIMEOUT)
                        obj.date = date
                        obj.subtitle = news.feed.subtitle
                        obj.put_async()
                    else:
                        error = _('Feed server send no entries')
                else:
                    error = _('Feed server returns %s' % feed.bozo_exception)
            else:
                error = _('Feed server returns %s' % future.get_exception())

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
    @login_required
    def get(self, form=None):
        if form is None:
            form = AddForm()
        self.render_template('admin/feed_form.html', {'form': form, 'filter': None})

    @csrf_protected
    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Feed(id=form.slug.data)
            obj.add(form.data)
            self.redirect_to('feed_admin')
        else:
            self.render_template('admin/feed_form.html', {'form': form, 'filter': None})


class Edit(BaseHandler):
    @login_required
    def get(self, slug, form=None):
        obj = Feed.get_by_id(slug)
        if not any([self.is_admin, self.user == obj.author]):
            self.abort(403)
        if form is None:
            form = EditForm(obj=obj)
        self.render_template('admin/feed_form.html', {'form': form, 'object': obj, 'filter': None})

    @csrf_protected
    def post(self, slug):
        obj = Feed.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect_to('feed_admin')
        else:
            self.render_template('admin/feed_form.html', {'form': form, 'object': obj, 'filter': None})