import uuid

from google.appengine.ext import ndb
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required

from wtforms import Form, fields, validators
from models import Comment
from handlers import BaseHandler
from common import Paginator, Filter
from settings import HOST


PER_PAGE = 10


class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Comment._properties[k] == v for k, v in f.parameters.items()]
        query = Comment.query(*filters).order(-Comment.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query, per_page=PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('comment/index.html', data)


class AddForm(Form):
    body = fields.TextAreaField(_('Comment'), validators=[validators.DataRequired()])


class Add(BaseHandler):
    @login_required
    def get(self, safe_key):
        form = AddForm()
        self.session['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, HOST).hex
        for_headline = ndb.Key(urlsafe=safe_key).get().headline
        self.render_template('snippets/addcomment.html',
                             {'form': form, 'safe_key': safe_key, 'headline': for_headline})

    def post(self, safe_key):
        try:
            assert self.session.get('uuid', None) == uuid.uuid5(uuid.NAMESPACE_DNS, HOST).hex
        except AssertionError:
            self.session.pop('uuid', None)
            self.abort(403)
        else:
            form = AddForm(formdata=self.request.POST)
            if form.validate():
                for_key = ndb.Key(urlsafe=safe_key)
                obj = Comment(
                    parent=for_key,
                    forkind=for_key.kind(),
                    body=form.data['body'])
                obj.add()
                self.session.pop('uuid', None)
                self.render_template('snippets/comment.html', {'comment': obj})
            else:
                self.render_json(form.errors)