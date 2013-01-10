import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from webapp2_extras.i18n import lazy_gettext as _
from wtforms import Form, widgets, FormField, FieldList, fields, validators
from models import Entry, ENTRY_IMAGES
from common import  BaseHandler, Paginator, Filter, TagsField, EmailField, make_thumbnail
from settings import LIMIT, TIMEOUT
PER_PAGE = 6

class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Entry._properties[k] == v for k, v in f.parameters.items()]
        query = Entry.query(*filters).order(-Entry.date)

        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query, per_page=PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'kind': 'Entry',
                'objects': objects,
                'filter': f.parameters,
                'filter_url': f.url,
                'filter_title': f.title,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('entry/index.html', data)

class Detail(BaseHandler):
    def get(self, slug):
        obj = Entry.get_by_id(slug)
        if obj is None:
            webapp2.abort(404)
        self.render_template('entry/detail.html', {'object': obj, 'filter': None})

#class BaseImgFormSet(BaseFormSet):
#    def add_fields(self, form, index):
#        super(BaseImgFormSet, self).add_fields(form, index)
#        if self.can_order:
#            if index < self.initial_forms:
#                form.fields['ORDER'] = forms.IntegerField(initial=index, required=False,
#                                                widget=forms.HiddenInput())
#            else:
#                form.fields['ORDER'] = forms.IntegerField(required=False,
#                                                widget=forms.HiddenInput())
#        if self.can_delete:
#            form.fields['DELETE'] = forms.BooleanField(label=_(u'delete'), required=False,
#                                                widget=forms.CheckboxInput(attrs={'style': 'margin-left: 80px;'}))
#
class ImgForm(Form):
    name = fields.TextField(_('Img.'), validators=[validators.DataRequired()])
    blob = fields.FileField()
#class AddImgForm(forms.Form):
#    name = forms.CharField(label=_('Img.'),
#                    widget=forms.TextInput(attrs={'style': 'width: 250px;'}),
#                    error_messages={'required': _('Required field')})
#    blob =  forms.FileField(error_messages={'required': _('Upload the image')})
#
#    def clean_blob(self):
#        data = self.cleaned_data['blob']
#        if data.size > LIMIT/4:
#            raise forms.ValidationError(_('Image too big, %s' % defaultfilters.filesizeformat(data.size)))
#        if data.content_type not in ['image/jpeg', 'image/png']:
#            raise forms.ValidationError(_('Only JPEG/PNG images allowed'))
#        return data
#
#class EditImgForm(forms.Form):
#    name = forms.CharField(label=_('Img.'), required=False,
#                    widget=forms.TextInput(attrs={'style': 'width: 250px;'}))
#    blob =  forms.FileField(required=False)
#
#    def clean(self):
#        data = self.cleaned_data
#        blob = data.get('blob', None)
#
#        if blob:
#            if blob.size > LIMIT/4:
#                self._errors['blob'] = _('Photo too big, %s') % defaultfilters.filesizeformat(blob.size)
#            if blob.content_type not in ['image/jpeg', 'image/png']:
#                self._errors['blob'] = _('Only JPEG/PNG images allowed')
#            if data['name'] == '':
#                self._errors['name'] = _('Required field')
#        return data
#
#AddImgFormSet = formset_factory(AddImgForm, extra=2, max_num=ENTRY_IMAGES)
#EditImgFormSet = formset_factory(EditImgForm, formset=BaseImgFormSet,
#                                 extra=2, can_order=True, can_delete=True, max_num=ENTRY_IMAGES)
#

class AddForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    slug = fields.TextField(_('Slug'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    summary = fields.TextAreaField(_('Summary'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Posted'), validators=[validators.DataRequired()])
    body = fields.TextAreaField(_('Article'), validators=[validators.DataRequired()])
    images = FieldList(FormField(ImgForm), min_entries=0, max_entries=10)

    def validate_slug(self, field):
        if Entry.get_by_id(field.data):
            raise validators.ValidationError(_('Record with this slug already exist'))

#    def validate_photo(self, field):
#        if not isinstance(field.data, cgi.FieldStorage):
#            raise validators.ValidationError(_('Not cgi.FieldStorage type.'))

#class AddForm(forms.Form):
#    summary = forms.CharField(label=_('Summary'),
#                    widget=forms.Textarea(attrs={'rows': 4, 'cols': 16}),
#                    error_messages={'required': _('Required field')})
#    body = forms.CharField(label=_('Article'),
#                    widget=forms.Textarea(attrs={'rows': 12, 'cols': 16}),
#                    error_messages={'required': _('Required field')})
#
class EditForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    summary = fields.TextAreaField(_('Summary'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Posted'), validators=[validators.DataRequired()])
    body = fields.TextAreaField(_('Article'), validators=[validators.DataRequired()])
    images = FieldList(FormField(ImgForm), min_entries=0, max_entries=10)

class Add(BaseHandler):
    def get(self):
        form = AddForm()
        self.render_template('entry/form.html', {'form': form, 'object': None, 'filter': None})

class Edit(BaseHandler):
    def get(self, slug, form=None):
        obj = Entry.get_by_id(slug)
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                webapp2.abort(403)
        if form is None:
            form = EditForm(obj=obj)
#            subform = ImgForm(imgs=obj.image_list)
#            form.images = obj.image_list
        self.render_template('entry/form.html', {'form': form, 'subform': None, 'object': obj, 'filter': None})

#@login_required
#def add(request, tmpl='entry/form.html'):
#    data = {}
#    if request.method == 'POST':
#        form = AddForm(request.POST, request.FILES)
#        formset = AddImgFormSet(request.POST, request.FILES)
#        if form.is_valid() and formset.is_valid():
#            data = form.cleaned_data
#            data['images'] = formset.cleaned_data
#            obj = Entry(id=data['slug'],
#                        headline=data['headline'],
#                        summary = data['summary'],
#                        body=data['body'])
#            obj.add(data)
#            if request.POST.get('action:continue'):
#                return redirect('%s/edit' % obj.get_absolute_url())
#            return redirect('/entries')
#    else:
#        form = AddForm()
#        formset = AddImgFormSet()
#
#    form.fields['front'] = forms.TypedChoiceField(required=False, choices=[],
#                                    coerce=int, empty_value=-1,
#                                    widget=forms.RadioSelect(choices=[]))
#    data['form'] = form
#    data['formset'] = formset
#    return render(request, tmpl, data)
#
#@login_required
#def edit(request, slug, tmpl='entry/form.html'):
#    obj = Entry.get_by_id(slug)
#    user = users.get_current_user()
#    is_admin = users.is_current_user_admin()
#    if not is_admin:
#        if user != obj.author:
#            raise PermissionDenied
#
#    data = {'object': obj}
#    formset_initial = [{'name': x.name, 'ORDER': x.num} for x in obj.image_list]
#    front_choices = [(x['ORDER'], x['name']) for x in formset_initial]
#    front_choices.append((-1, _('None')))
#
#    if request.method == 'POST':
#        form = EditForm(request.POST, request.FILES)
#        formset = EditImgFormSet(request.POST, request.FILES,
#                                 initial=formset_initial)
#        if form.is_valid() and formset.is_valid():
#            newdata = form.cleaned_data
#            newdata['front'] = request.POST.get('front')
#            newdata['images'] = formset.cleaned_data
#            data.update(newdata)
#            obj.edit(data)
#            if request.POST.get('action:continue'):
#                return redirect('%s/edit' % obj.get_absolute_url())
#            return redirect(obj.get_absolute_url())
#    else:
#        form = EditForm(initial={'headline': obj.headline,
#                                 'slug': obj.key.string_id(),
#                                 'tags': ', '.join(obj.tags),
#                                 'summary': obj.summary,
#                                 'date': obj.date,
#                                 'body': obj.body})
#        formset = EditImgFormSet(initial=formset_initial)
#
#    form.fields['front'] = forms.TypedChoiceField(required=False, choices=front_choices,
#                                    coerce=int, empty_value=-1,
#                                    widget=forms.RadioSelect(choices=front_choices))
#    form.fields['front'].initial = obj.front
#
#    data['form'] = form
#    data['formset'] = formset
#    return render(request, tmpl, data)

def thumb(request, slug, size):
    out, mime = make_thumbnail('Entry', slug, size)
    if out:
        response = webapp2.Response(content_type=mime)
        response.headers['Cache-Control'] = 'public, max-age=%s' % (TIMEOUT*600)
        if size == 'normal':
            response.headers['Content-Disposition'] = 'inline; filename=%s' % slug
        response.out.write(out)
        return response
    else:
        webapp2.abort(503)