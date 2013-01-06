import webapp2, json
from google.appengine.api import users
from google.appengine.ext import ndb, deferred
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form, widgets, fields, validators
from models import Comment
from common import  BaseHandler, Paginator, Filter, EmailField
from settings import LIMIT, TIMEOUT
PER_PAGE = 10
import logging

class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Comment._properties[k] == v for k, v in f.parameters.items()]
        query = Comment.query(*filters).order(-Comment.date)

        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query, per_page=PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'kind': 'Comment',
                'objects': objects,
                'filter': f.parameters,
                'filter_url': f.url,
                'filter_title': f.title,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('comment/index.html', data)

class AddForm(Form):
    email = fields.TextField(_('e-mail'), validators=[validators.DataRequired(), validators.Email()])
    body = fields.TextAreaField(_('Comment'), validators=[validators.DataRequired()])

#class CommentForm(forms.Form):
#    def clean_email(self):
#        data = self.cleaned_data['email']
#        if not data:
#            user = users.get_current_user()
#            if user:
#                data = user.email()
#            else:
#                raise forms.ValidationError(_('Required field'))
#        return data
#
def send(safekey, email, body):
    key = ndb.Key(urlsafe=safekey)
    obj = Comment(parent=key,
                  author = users.User(email),
                  forkind = key.kind(),
                  body=body)
    obj.add()
#
#def validate(request):
#    if request.is_ajax():
#        params = request.POST
#        form = CommentForm(params)
#        if form.is_valid():
#            data = form.cleaned_data
#            #{u'data': [{u'body': u''}], u'key': u'agRh...'}
#            args = [params['safekey'], data['email'], data['body']]
#            deferred.defer(send, *args)
#            return json_response({'success': True})
#
#        ret = {}
#        for k, v in form.errors.items():
#            ret[k] = v.as_text()
#        return json_response(ret)
#

class Validate(BaseHandler):
    def post(self):
        form = AddForm(self.request.POST)
        logging.error(form.data)

        if form.validate():
            data = dict(form.data)
            logging.error(data)
            deferred.defer(send, data['safekey'], data['email'], data['body'])
            self.response = webapp2.Response(content_type='application/json')
            self.response.out.write(json.dumps({'success': True}))
        else:
            self.response = webapp2.Response(content_type='application/json')
            self.response.out.write(json.dumps(form.errors))

class Add(BaseHandler):
    def get(self, safekey, form=None):
        refobj = ndb.Key(urlsafe=safekey).get()
        user = users.get_current_user()
        if form is None:
            if user:
                form = AddForm(**{'email': user.email()})
            else:
                form = AddForm()
        self.render_template('snippets/addcomment.html', {'form': form, 'refobj': refobj})

#def add(request, safekey, tmpl='snippets/addcomment.html'):
#    if request.is_ajax():
#        form = CommentForm()
#        refobj = ndb.Key(urlsafe=safekey).get()
#        user = users.get_current_user()
#        if user:
#            form.fields['email'].initial = user.email()
#        data = {'refobj': refobj, 'form': form}
#        return render(request, tmpl, data)