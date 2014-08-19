from google.appengine.ext import ndb
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required

from wtforms import Form, fields, validators
from models import Comment
from handlers import BaseHandler, csrf_protected, Paginator, parameters, touch_appcache


class Index(BaseHandler):
    def get(self, page=1, field=None, value=None):
        f = parameters(field, value)
        filters = [Comment._properties[k] == v for k, v in f.items()]
        query = Comment.query(*filters).order(-Comment.date)

        page = int(page)
        paginator = Paginator(query)
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
        for_headline = ndb.Key(urlsafe=safe_key).get().headline
        self.render_template('snippets/addcomment.html',
                             {'form': form, 'safe_key': safe_key, 'headline': for_headline})

    @csrf_protected
    @touch_appcache
    def post(self, safe_key):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            for_key = ndb.Key(urlsafe=safe_key)
            obj = Comment(
                parent=for_key,
                forkind=for_key.kind(),
                body=form.data['body'])
            obj.add()
            self.render_template('snippets/comment.html', {'comment': obj})
        else:
            self.render_json(form.errors)