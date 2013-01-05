import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb, deferred
#from django.shortcuts import redirect, render
#from django.core.exceptions import PermissionDenied
#from django.utils.translation import gettext_lazy as _
#from django import forms
from models import Comment
#from lib.comm import Paginator, Filter, login_required, json_response
from common import  LIMIT, TIMEOUT, BaseHandler, Paginator, Filter
PER_PAGE = 10

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

#class CommentForm(forms.Form):
#    email = forms.EmailField(label='e-mail', required=True,
#                    widget=forms.TextInput(),
#                    error_messages={'required': _('Required field'),
#                                    'invalid': _('Enter a valid e-mail address')})
#    body = forms.CharField(label=_('Comment'),
#                    widget=forms.Textarea(attrs={'rows': 6, 'cols': 16}),
#                    error_messages={'required': _('Required field')})
#
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
#def send(safekey, email, body):
#    key = ndb.Key(urlsafe=safekey)
#    obj = Comment(parent=key,
#                  author = users.User(email),
#                  forkind = key.kind(),
#                  body=body)
#    obj.add()
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
#def add(request, safekey, tmpl='snippets/addcomment.html'):
#    if request.is_ajax():
#        form = CommentForm()
#        refobj = ndb.Key(urlsafe=safekey).get()
#        user = users.get_current_user()
#        if user:
#            form.fields['email'].initial = user.email()
#        data = {'refobj': refobj, 'form': form}
#        return render(request, tmpl, data)