import datetime
from google.appengine.api import users
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.template import defaultfilters
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import gettext_lazy as _
from django import forms
from models import Photo
from lib.comm import Paginator, Filter, login_required, make_thumbnail
from django.conf import settings

FAMILY = ['mihailo.genije@gmail.com', 'milan.andrejevic@gmail.com',
          'svetlana.andrejevic@gmail.com', 'ana.devic@gmail.com']

def index(request, field=None, value=None, tmpl='photo/index.html'):
    f = Filter(field, value)
    filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
    query = Photo.query(*filters).order(-Photo.date)
    
    page = int(request.GET.get('page', 1))
    paginator = Paginator(query)
    objects, has_next = paginator.page(page)

    data = {'kind': 'Photo',
            'objects': objects,
            'filter': f.parameters,
            'filter_url': f.url,
            'filter_title': f.title,
            'page': page,
            'has_next': has_next,
            'has_previous': page > 1}
    return render(request, tmpl, data)

def detail(request, slug, field=None, value=None, tmpl='photo/detail.html'):
    if 'page' not in request.GET or 'pic' not in request.GET:
        obj = Photo.get_by_id(slug)
        if obj is None:
            raise Http404
        return render(request, tmpl, {'object': obj, 'next': None, 'previous': None, 'page': 1})
    
    f = Filter(field, value)
    filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
    query = Photo.query(*filters).order(-Photo.date)
    
    page = int(request.GET.get('page', 1))
    pic = int(request.GET.get('pic', 1))
    paginator = Paginator(query)
    previous, obj, next, numbers = paginator.triple(page, pic)
    
    data = {'object': obj,
            'next': next,
            'previous': previous,
            'filter': f.parameters,
            'filter_url': f.url,
            'filter_title': f.title,
            'page': page,
            'num': (page - 1)*paginator.per_page + pic,
            'numbers': numbers}
    return render(request, tmpl, data)

class AddForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                    error_messages={'required': _('Required field')})
    slug = forms.SlugField(label=_('Slug'), error_messages={'required': _('Required field')})
    tags = forms.CharField(label=_('Tags'), required=False)
    photo = forms.FileField(label=_('Photo'), error_messages={'required': _('Upload the photo')})

    def clean_slug(self):
        data = self.cleaned_data['slug']
        if Photo.get_by_id(data):
            raise forms.ValidationError(_("Record with this slug already exist"))
        return data

    def clean_photo(self):
        data = self.cleaned_data['photo']
        if data.content_type != 'image/jpeg':
            raise forms.ValidationError(_('Only JPEG photos allowed'))
        elif data.size > settings.LIMIT:
            raise forms.ValidationError(_('Photo too big, %s' % defaultfilters.filesizeformat(data.size)))
        return data

class EditForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                error_messages={'required': _('Required field')})
    tags = forms.CharField(label=_('Tags'), required=False)
    author = forms.CharField(label=_('Author'), required=True)

    model = forms.CharField(label=_('Camera model'), required=False)
    aperture = forms.FloatField(label=_('Aperture'), required=False)
    shutter = forms.CharField(label=_('Shutter speed'), required=False)
    focal_length = forms.FloatField(label=_('Focal length'), required=False)
    iso = forms.IntegerField(label='%s (ISO)' % _('Sensitivity'), required=False)
    date = forms.DateTimeField(label=_('Taken'), widget=AdminSplitDateTime())
    crop_factor = forms.FloatField(label=_('Crop factor'), required=False)
    lens = forms.CharField(label=_('Lens type'), required=False)

@login_required
def add(request, tmpl='photo/form.html'):
    data = {}
    if request.method == 'POST':
        form = AddForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            obj = Photo(id=data['slug'], headline=data['headline'])
            obj.add(data)
            return redirect('%s/edit' % obj.get_absolute_url())
    else:
        form = AddForm()

    data['form'] = form
    return render(request, tmpl, data)

@login_required
def edit(request, slug, tmpl='photo/form.html'):
    obj = Photo.get_by_id(slug)
    user = users.get_current_user()
    is_admin = users.is_current_user_admin()
    if not is_admin:
        if user != obj.author:
            raise PermissionDenied

    data = {'object': obj}
    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            obj.edit(data)
            return redirect(obj.get_absolute_url())
    else:
        form = EditForm(initial={
            'headline': obj.headline,
            'tags': ', '.join(obj.tags),
            'model': obj.model,
            'aperture': obj.aperture,
            'shutter': obj.shutter,
            'focal_length': obj.focal_length,
            'iso': obj.iso,
            'date': obj.date or datetime.datetime.now(),
            'crop_factor': obj.crop_factor,
            'lens': obj.lens})
        email = obj.author.email()
        if not email in FAMILY:
            FAMILY.append(email)
        form.fields['author'] = forms.ChoiceField(label=_('Author'), choices=[(x, x) for x in FAMILY], required=True)
        form.fields['author'].initial = email

    data['form'] = form
    return render(request, tmpl, data)

@login_required
def delete(request, slug, tmpl='snippets/confirm.html'):
    obj = Photo.get_by_id(slug)
    user = users.get_current_user()
    is_admin = users.is_current_user_admin()
    if not is_admin:
        if user != obj.author:
            raise PermissionDenied

    if request.method == 'POST':
        obj.key.delete()
        return redirect('/photos')
    elif request.is_ajax():
        data = {'object': obj, 'post_url': request.path}
        return render(request, tmpl, data)

def thumb(request, slug, size):
    out, mime = make_thumbnail('Photo', slug, size)
    if out:
        response = HttpResponse(mimetype=mime)
        response['Cache-Control'] = 'public, max-age=%s' % (settings.TIMEOUT*600)
        if size == 'normal':
            response['Content-Disposition'] = 'inline; filename=%s' % slug
        response.write(out)
        return response
    else:
        return HttpResponse(status=503)
