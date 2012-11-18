from google.appengine.api import users
from google.appengine.ext import ndb
from django.template import defaultfilters
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.contrib.admin.widgets import AdminSplitDateTime
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from models import Entry, ENTRY_IMAGES
from lib.comm import Paginator, Filter, login_required, make_thumbnail
from django.conf import settings
PER_PAGE = 6

def index(request, field=None, value=None, tmpl='entry/index.html'):
    f = Filter(field, value)
    filters = [Entry._properties[k] == v for k, v in f.parameters.items()]
    query = Entry.query(*filters).order(-Entry.date)

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

def detail(request, slug, tmpl='entry/detail.html'):
    obj = Entry.get_by_id(slug)
    if obj is None:
        raise Http404
    return render(request, tmpl, {'object': obj})

class BaseImgFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super(BaseImgFormSet, self).add_fields(form, index)
        if self.can_order:
            if index < self.initial_forms:
                form.fields['ORDER'] = forms.IntegerField(initial=index, required=False,
                                                widget=forms.HiddenInput())
            else:
                form.fields['ORDER'] = forms.IntegerField(required=False,
                                                widget=forms.HiddenInput())
        if self.can_delete:
            form.fields['DELETE'] = forms.BooleanField(label=_(u'delete'), required=False,
                                                widget=forms.CheckboxInput(attrs={'style': 'margin-left: 80px;'}))

class AddImgForm(forms.Form):
    name = forms.CharField(label=_('Img.'),
                    widget=forms.TextInput(attrs={'style': 'width: 250px;'}),
                    error_messages={'required': _('Required field')})
    blob =  forms.FileField(error_messages={'required': _('Upload the image')})

    def clean_blob(self):
        data = self.cleaned_data['blob']
        if data.size > settings.LIMIT/4:
            raise forms.ValidationError(_('Image too big, %s' % defaultfilters.filesizeformat(data.size)))
        if data.content_type not in ['image/jpeg', 'image/png']:
            raise forms.ValidationError(_('Only JPEG/PNG images allowed'))
        return data

class EditImgForm(forms.Form):
    name = forms.CharField(label=_('Img.'), required=False,
                    widget=forms.TextInput(attrs={'style': 'width: 250px;'}))
    blob =  forms.FileField(required=False)

    def clean(self):
        data = self.cleaned_data
        blob = data.get('blob', None)

        if blob:
            if blob.size > settings.LIMIT/4:
                self._errors['blob'] = _('Photo too big, %s') % defaultfilters.filesizeformat(blob.size)
            if blob.content_type not in ['image/jpeg', 'image/png']:
                self._errors['blob'] = _('Only JPEG/PNG images allowed')
            if data['name'] == '':
                self._errors['name'] = _('Required field')
        return data

AddImgFormSet = formset_factory(AddImgForm, extra=2, max_num=ENTRY_IMAGES)
EditImgFormSet = formset_factory(EditImgForm, formset=BaseImgFormSet,
                                 extra=2, can_order=True, can_delete=True, max_num=ENTRY_IMAGES)

class AddForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                    error_messages={'required': _('Required field')})
    slug = forms.SlugField(label=_('Slug'), error_messages={'required': _('Required field')})
    tags = forms.CharField(label=_('Tags'), required=False)
    summary = forms.CharField(label=_('Summary'),
                    widget=forms.Textarea(attrs={'rows': 4, 'cols': 16}),
                    error_messages={'required': _('Required field')})
    date = forms.DateTimeField(label=_('Posted'), widget=AdminSplitDateTime())
    body = forms.CharField(label=_('Article'),
                    widget=forms.Textarea(attrs={'rows': 12, 'cols': 16}),
                    error_messages={'required': _('Required field')})

    def clean_slug(self):
        data = self.cleaned_data['slug']
        if Entry.get_by_id(data):
            raise forms.ValidationError(_('Record with this slug already exist'))
        return data

class EditForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                error_messages={'required': _('Required field')})
    slug = forms.SlugField(label=_('Slug'), required=False,
                widget=forms.TextInput(attrs={'disabled': 'disabled', 'class': 'disabled'}))
    tags = forms.CharField(label=_('Tags'), required=False)
    summary = forms.CharField(label=_('Summary'),
                    widget=forms.Textarea(attrs={'rows': 4, 'cols': 16}),
                    error_messages={'required': _('Required field')})
    date = forms.DateTimeField(label=_('Posted'), widget=AdminSplitDateTime())
    body = forms.CharField(label=_('Article'),
                    widget=forms.Textarea(attrs={'rows': 12, 'cols': 16}),
                    error_messages={'required': _('Required field')})

    def clean(self):
        data = self.cleaned_data
        return data

@login_required
def add(request, tmpl='entry/form.html'):
    data = {}
    if request.method == 'POST':
        form = AddForm(request.POST, request.FILES)
        formset = AddImgFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            data['images'] = formset.cleaned_data
            obj = Entry(id=data['slug'],
                        headline=data['headline'],
                        summary = data['summary'],
                        body=data['body'])
            obj.add(data)
            if request.POST.get('action:continue'):
                return redirect('%s/edit' % obj.get_absolute_url())
            return redirect('/entries')
    else:
        form = AddForm()
        formset = AddImgFormSet()

    form.fields['front'] = forms.TypedChoiceField(required=False, choices=[],
                                    coerce=int, empty_value=-1,
                                    widget=forms.RadioSelect(choices=[]))
    data['form'] = form
    data['formset'] = formset
    return render(request, tmpl, data)

@login_required
def edit(request, slug, tmpl='entry/form.html'):
    obj = Entry.get_by_id(slug)
    user = users.get_current_user()
    is_admin = users.is_current_user_admin()
    if not is_admin:
        if user != obj.author:
            raise PermissionDenied

    data = {'object': obj}
    formset_initial = [{'name': x.name, 'ORDER': x.num} for x in obj.image_list]
    front_choices = [(x['ORDER'], x['name']) for x in formset_initial]
    front_choices.append((-1, _('None')))

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES)
        formset = EditImgFormSet(request.POST, request.FILES,
                                 initial=formset_initial)
        if form.is_valid() and formset.is_valid():
            newdata = form.cleaned_data
            newdata['front'] = request.POST.get('front')
            newdata['images'] = formset.cleaned_data
            data.update(newdata)
            obj.edit(data)
            if request.POST.get('action:continue'):
                return redirect('%s/edit' % obj.get_absolute_url())
            return redirect(obj.get_absolute_url())
    else:
        form = EditForm(initial={'headline': obj.headline,
                                 'slug': obj.key.string_id(),
                                 'tags': ', '.join(obj.tags),
                                 'summary': obj.summary,
                                 'date': obj.date,
                                 'body': obj.body})
        formset = EditImgFormSet(initial=formset_initial)

    form.fields['front'] = forms.TypedChoiceField(required=False, choices=front_choices,
                                    coerce=int, empty_value=-1,
                                    widget=forms.RadioSelect(choices=front_choices))
    form.fields['front'].initial = obj.front
    
    data['form'] = form
    data['formset'] = formset
    return render(request, tmpl, data)

@login_required
def delete(request, slug, tmpl='snippets/confirm.html'):
    obj = Entry.get_by_id(slug)
    user = users.get_current_user()
    is_admin = users.is_current_user_admin()
    if not is_admin:
        if user != obj.author:
            raise PermissionDenied

    if request.method == 'POST':
        obj.delete()
        return redirect('/entries')
    elif request.is_ajax():
        data = {'object': obj, 'post_url': request.path}
        return render(request, tmpl, data)

def thumb(request, slug, size):
    out, mime = make_thumbnail('Entry', slug, size)
    if out:
        response = HttpResponse(mimetype=mime)
        response['Cache-Control'] = 'public, max-age=%s' % (settings.TIMEOUT*600)
        if size == 'normal':
            response['Content-Disposition'] = 'inline; filename=%s' % slug
        response.write(out)
        return response
    else:
        return HttpResponse(status=503)
