import datetime
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb, blobstore
#from django.shortcuts import redirect, render
#from django.core.exceptions import PermissionDenied
#from django.contrib.admin.widgets import AdminSplitDateTime
from webapp2_extras.i18n import lazy_gettext as _
#from django import forms
from models import Photo
from common import TIMEOUT, BaseHandler, Paginator, Filter, make_thumbnail
import logging

FAMILY = ['mihailo.genije@gmail.com', 'milan.andrejevic@gmail.com',
          'svetlana.andrejevic@gmail.com', 'ana.devic@gmail.com', 'dannytaboo@gmail.com']

class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.GET.get('page', 1))
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
        self.render_template('photo/index.html', data)

class Detail(BaseHandler):
    def get(self, slug, field=None, value=None):
        if 'page' not in self.request.GET or 'pic' not in self.request.GET:
            obj = Photo.get_by_id(slug)
            if obj is None:
                webapp2.abort(404)
            self.render_template('photo/detail.html',
                {'object': obj, 'next': None, 'previous': None, 'page': 1})

        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.GET.get('page', 1))
        pic = int(self.request.GET.get('pic', 1))
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
        self.render_template('photo/detail.html', data)

#class AddForm(forms.Form):
#    headline = forms.CharField(label=_('Headline'),
#        error_messages={'required': _('Required field')})
#    slug = forms.SlugField(label=_('Slug'), error_messages={'required': _('Required field')})
#    tags = forms.CharField(label=_('Tags'), required=False)
#    author = forms.CharField(label=_('Author'), required=True)
#    photo = forms.FileField(label=_('Photo'), error_messages={'required': _('Upload the photo')})
#
#    def clean_slug(self):
#        data = self.cleaned_data['slug']
#        if Photo.get_by_id(data):
#            raise forms.ValidationError(_("Record with this slug already exist"))
#        return data
#
#class EditForm(forms.Form):
#    headline = forms.CharField(label=_('Headline'),
#                error_messages={'required': _('Required field')})
#    tags = forms.CharField(label=_('Tags'), required=False)
#    author = forms.CharField(label=_('Author'), required=True)
#    date = forms.DateTimeField(label=_('Taken'), widget=AdminSplitDateTime(), required=True)
#    model = forms.CharField(label=_('Camera model'), required=False)
#    aperture = forms.FloatField(label=_('Aperture'), required=False)
#    shutter = forms.CharField(label=_('Shutter speed'), required=False)
#    focal_length = forms.FloatField(label=_('Focal length'), required=False)
#    iso = forms.IntegerField(label='%s (ISO)' % _('Sensitivity'), required=False)
#    crop_factor = forms.FloatField(label=_('Crop factor'), required=False)
#    lens = forms.CharField(label=_('Lens type'), required=False)

#@login_required
#def add(request, tmpl='photo/form.html'):
#    user = users.get_current_user()
    # 1 step
#    if request.method == 'POST':
#        form = AddForm(request.POST, request.FILES)
#        logging.error(request.FILES)
#        if form.is_valid():
#            data = form.cleaned_data
#            blob_info = blobstore.parse_blob_info(request.FILES)
#            obj = Photo(id=data['slug'], headline=data['headline'])
#            data['blob_key'] = blob_info.key()
#            obj.add(data)
#            return redirect('%s/edit' % obj.get_absolute_url())
#    else:
#    form = AddForm()
#    email = user.email()
#    if not email in FAMILY:
#        FAMILY.append(email)
#    form.fields['author'] = forms.ChoiceField(label=_('Author'), choices=[(x, x) for x in FAMILY], required=True)
#    form.fields['author'].initial = email
##        form.fields['headline'].initial = blobstore.BlobInfo.get(blob_key).filename
#    return render(request, tmpl, {
#        'form': form,
#        'upload_url': blobstore.create_upload_url('/upload')
#        })

#@login_required
#def edit(request, slug, tmpl='photo/form.html'):
#    obj = Photo.get_by_id(slug)
#    user = users.get_current_user()
#    is_admin = users.is_current_user_admin()
#    if not is_admin:
#        if user != obj.author:
#            raise PermissionDenied
#
#    if request.method == 'POST':
#        # 5 step
#        form = EditForm(request.POST)
#        if form.is_valid():
#            data = form.cleaned_data
#            obj.edit(data)
#            return redirect(obj.get_absolute_url())
#    else:
#        # 4 step
#        form = EditForm()
#        email = obj.author.email()
#        if not email in FAMILY:
#            FAMILY.append(email)
#        form.fields['author'] = forms.ChoiceField(label=_('Author'), choices=[(x, x) for x in FAMILY], required=True)
#        form.initial = {
#            'headline': obj.headline,
#            'slug': obj.key.string_id(),
#            'tags': ', '.join(obj.tags),
#            'author': email,
#            'model': obj.model,
#            'aperture': obj.aperture,
#            'shutter': obj.shutter,
#            'focal_length': obj.focal_length,
#            'iso': obj.iso,
#            'date': obj.date or datetime.datetime.now(),
#            'crop_factor': obj.crop_factor,
#            'lens': obj.lens}
#
#    return render(request, tmpl, {
#        'form': form,
#        'object': obj
#    })

class Delete(BaseHandler):
#    @login_required
    def get(self, slug):
        obj = Photo.get_by_id(slug)
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                webapp2.abort(403)
        data = {'object': obj, 'post_url': self.path}
        self.render_template('snippets/confirm.html', data)

    def post(self, key): # TODO get key
        key.delete()
        self.redirect('/photos')

def thumb(request, slug, size):
    out, mime = make_thumbnail('Photo', slug, size)
    if out:
        response = webapp2.Response(content_type=mime)
        response.headers['Cache-Control'] = 'public, max-age=%s' % (TIMEOUT*600)
        if size == 'normal':
            response.headers['Content-Disposition'] = 'inline; filename=%s' % slug
        response.out.write(out)
        return response
    else:
        webapp2.abort(503)