import datetime, time
from cStringIO import StringIO
from google.appengine.api import images, users
from google.appengine.ext import ndb
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.template import defaultfilters
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import gettext_lazy as _
from django import forms
from models import Photo
from lib.comm import Paginator, Filter, login_required, make_thumbnail
from lib.EXIF import process_file
from django.conf import settings

FAMILY = ['milan.andrejevic@gmail.com', 'svetlana.andrejevic@gmail.com', 
          'ana.devic@gmail.com', 'mihailo.genije@gmail.com']
PROGRAMS = [(x, x) for x in ('', 'Manual', 'Program Normal', 'Aperture Priority',
                             'Shutter Priority', 'Program Creative',
                             'Program Action', 'Portrait Mode', 'Landscape Mode')]

"""
http://www.media.mit.edu/pia/Research/deepview/exif.html

img = images.Image(buff)
img.rotate(0)
img.execute_transforms(output_encoding=images.JPEG, parse_source_metadata=True)
img.get_original_metadata() =

 canon 400d

 u'YResolution': 72, 
 u'ResolutionUnit': 2, '1' means no-unit, '2' inch, '3' centimeter.
 u'Aritst': u'Mihailo Andrejevic', 
 u'Make': u'Canon', 
 u'Flash': 1, <---------------------------------
 u'SerialNumber': u'1981155104', 
 u'SceneCaptureType': 0, 
 u'DateTime': u'2012:01:18 20:55:19', <---------------------------------
 u'FlashMode': 1, 
 u'MeteringMode': 5,  '1' means average, '2' center weighted average, '3' spot, '4' multi-spot, '5' multi-segment.
 u'XResolution': 72, 
 u'ExposureBiasValue': 0, 
 u'FlashCompensation': 0, 
 u'MimeType': 0, 
 u'ImageNumber': u'64', 
 u'ColorProfile': True, 
 u'ExposureProgram': 2, '1' means manual control, '2' program normal, '3' aperture priority, '4' shutter priority, '5' program creative (slow program), '6' program action(high-speed program), '7' portrait mode, '8' landscape mode.
 u'FocalLengthIn35mmFilm': 393, <---------------------------------
 u'ShutterSpeedValue': 5.9068908999999996, <--------------------------------- = 1/2^5.9 = 1/60
 u'ColorSpace': 255, 
 u'Lens': u'EF100mm f/2.8 Macro USM', <---------------------------------
 u'DateTimeDigitized': u'2012:01:18 21:29:07', 
 u'DateTimeOriginal': u'1326922147', 
 u'ImageWidth': 1600, 
 u'FocalPlaneResolutionUnit': 2, 
 u'WhiteBalance': 0, 
 u'TimeZoneOffset': [1, 1, 1], 
 u'OwnerName': u'Mihailo Andrejevic', 
 u'FNumber': 2.7999999999999998, <--------------------------------- = 2.8
 u'Firmware': u'1.1.1', 
 u'CustomRendered': 0, 
 u'ApertureValue': 2.9708540000000001,  = sqrt(2)^2.97 = 2.8
 u'FocalLength': 100, <---------------------------------
 u'ExposureMode': 0, 
 u'FocalPlaneXResolution': 4433.2954, 
 u'FlashFunction': False, 
 u'LensInfo': u'100/1 100/1 0/0 0/0', 
 u'ISOSpeedRatings': 100, <---------------------------------
 u'Model': u'Canon EOS 400D DIGITAL', <---------------------------------
 u'Software': u'Adobe Photoshop Lightroom', 
 u'ExposureTime': 0.016666667999999999, <--------------------------------- = 1/60
 u'ImageLength': 1067, 
 u'MaxApertureValue': 2.96875, 
 u'FlashReturn': 0, 
 u'TimeZoneMinutes': [0, 0, 0], 
 u'DateCreated': u'2012:01:18 21:29:07', 
 u'FlashRedEyeMode': True, 
 u'CCDWidth': 9.1669959999999993, 
 u'LensID': u'190'
 
 google nexus s
 
 u'GPSLongitude': 20.481388888888887,
 u'GPSTimeStamp': 3,
 u'GPSAltitude': 314,
 u'GPSDateStamp': u'2011:07:20',
 u'GPSLatitude': 44.79944444444444,
 u'TimeZoneOffset': [2, 2, 2]
 
"""

def populate_exif(buff):
    data = {}
    tags = process_file(StringIO(buff), details=False)
    if tags:
        if 'EXIF FNumber' in tags:
            data['aperture'] = round(float(eval('%s.0' % tags['EXIF FNumber'].printable)), 1)
        if 'EXIF DateTimeOriginal' in tags:
            dt_tuple = time.strptime(tags['EXIF DateTimeOriginal'].printable, '%Y:%m:%d %H:%M:%S')
            epochsec = time.mktime(dt_tuple)
            data['date'] = datetime.datetime.fromtimestamp(epochsec)
        
        if 'EXIF ExposureProgram' in tags:
            data['program'] = tags['EXIF ExposureProgram'].printable
        if 'EXIF ExposureTime' in tags:
            data['shutter'] = tags['EXIF ExposureTime'].printable
        if 'EXIF ISOSpeedRatings' in tags:
            data['iso'] = int(tags['EXIF ISOSpeedRatings'].printable)
        
#        doesn't exist
#        if 'EXIF Lens' in tags:
#            data['lens'] = tags['EXIF Lens'].printable.replace('/', '')
    
        if 'Image Make' in tags and 'Image Model' in tags:
            make = tags['Image Make'].printable.replace('/', '')
            model = tags['Image Model'].printable.replace('/', '')
            s1 = set(make.split())
            s2 = set(model.split())
            if not s1&s2:
                data['model'] = ' '.join(list(s1-s2) + list(s2-s1))
            else:
                data['model'] = model
        elif 'Image Model' in tags:
            data['model'] = tags['Image Model'].printable.replace('/', '')
    
        if 'EXIF FocalLength' in tags:
            value = float(eval('%s.0' % tags['EXIF FocalLength'].printable))
            data['focal_length'] = round(value, 1)
    
    return data

def index(request, field=None, value=None, tmpl='photo/index.html'):
    f = Filter(field, value)
    filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
    query = Photo.query(*filters).order(-Photo.date)
    
    page = int(request.GET.get('page', 1))
    paginator = Paginator(query)
    objects, has_next = paginator.page(page)

    data = {'objects': objects,
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
        buff = data.read()
        exif = populate_exif(buff)
        if not 'date' in exif:
            exif['date'] = datetime.datetime.now()
        return data, buff, exif

class EditForm(forms.Form):
    headline = forms.CharField(label=_('Headline'),
                error_messages={'required': _('Required field')})
    slug = forms.SlugField(label=_('Slug'), required=False,
                widget=forms.TextInput(attrs={'disabled': 'disabled', 'class': 'disabled'}))
    tags = forms.CharField(label=_('Tags'), required=False)
    photo = forms.FileField(label=_('Photo'), required=False)
    author = forms.CharField(label=_('Author'), required=True)

    model = forms.CharField(label=_('Camera model'), required=False)
    aperture = forms.FloatField(label=_('Aperture'), required=False)
    shutter = forms.CharField(label=_('Shutter speed'), required=False)
    focal_length = forms.FloatField(label=_('Focal length'), required=False)
    iso = forms.IntegerField(label='%s (ISO)' % _('Sensitivity'), required=False)
    date = forms.DateTimeField(label=_('Taken'), widget=AdminSplitDateTime())
    program = forms.ChoiceField(label=_('Program'), choices=PROGRAMS, required=False)
    crop_factor = forms.FloatField(label=_('Crop factor'), required=False)
    lens = forms.CharField(label=_('Lens type'), required=False)

    def clean(self):
        buff = ''
        exif = {}
        data = self.cleaned_data
        photo = data['photo']
        try:
            photo.content_type
        except:
            exif['model'] = data.get('model', None)
            exif['aperture'] = data.get('aperture', None)
            exif['shutter'] = data.get('shutter', None)
            exif['iso'] = data.get('iso', None)
            exif['program'] = data.get('program', None)
            exif['date'] = data['date']

            focal_length = data.get('focal_length', None)
            crop_factor = data.get('crop_factor', None)
            if focal_length and crop_factor:
                exif['focal_length'] = round(focal_length, 1)
                exif['crop_factor'] = round(crop_factor, 1)
                exif['eqv'] = int(10*round(focal_length*crop_factor/10))

            if data.get('lens', None):
                exif['lens'] = data['lens'].replace('/', '')
        else:
            if photo.content_type != 'image/jpeg':
                self._errors['photo'] = _('Only JPEG photos allowed')
            elif photo.size > settings.LIMIT:
                self._errors['photo'] = _('Photo too big, %s') % defaultfilters.filesizeformat(data.size)
            buff = photo.read()
            exif = populate_exif(buff)

        return data, buff, exif

@login_required
def add(request, tmpl='photo/form.html'):
    data = {}
    if request.method == 'POST':
        form = AddForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            x, buff, exif = data['photo']

            obj = Photo(id=data['slug'], headline=data['headline'])
            obj.add(data, buff, exif)
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
            newdata, buff, exif = form.cleaned_data
            if not buff and request.POST.get('action:exif'):
                buff = obj.picture.get().blob
                exif = populate_exif(buff)
                newdata.update(exif)

            data.update(newdata)
            obj.edit(data, buff, exif)
            if request.POST.get('action:exif') or request.POST.get('action:continue'):
                return redirect('%s/edit' % obj.get_absolute_url())
            return redirect(obj.get_absolute_url())
    else:
        form = EditForm(initial={'headline': obj.headline,
                                 'slug': obj.key.string_id(),
                                 'tags': ', '.join(obj.tags),
                                 'model': obj.model,
                                 'aperture': obj.aperture,
                                 'shutter': obj.shutter,
                                 'focal_length': obj.focal_length,
                                 'iso': obj.iso,
                                 'date': obj.date or datetime.datetime.now(),
                                 'program': obj.program,
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
