import json
from google.appengine.api import users
from google.appengine.ext import ndb
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form, fields, validators
from models import Comment
from handlers import BaseHandler
from common import Paginator, Filter

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
    email = fields.TextField(_('e-mail'), validators=[validators.DataRequired(), validators.Email()])
    body = fields.TextAreaField(_('Comment'), validators=[validators.DataRequired()])


class Add(BaseHandler):
    def get(self, safe_key):
        refobj = ndb.Key(urlsafe=safe_key).get()
        user = users.get_current_user()
        if user:
            form = AddForm(**{'email': user.email()})
        else:
            form = AddForm()
        self.render_template('snippets/addcomment.html',
                             {'form': form, 'safe_key': safe_key, 'headline': refobj.headline})

    def post(self, safe_key):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            refkey = ndb.Key(urlsafe=safe_key)
            obj = Comment(
                parent=refkey,
                author=users.User(form.data['email']),
                forkind=refkey.kind(),
                body=form.data['body'])
            obj.add()
            self.render_template('snippets/comment.html', {'comment': obj})
        else:
            self.response.content_type = 'application/json'
            self.response.write(json.dumps(form.errors))